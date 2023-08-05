import Acquisition
import urllib
import os
import lovely.tag.browser.tag
from lovely.tag.interfaces import ITaggingEngine, ITagging
from zope.formlib import form
from zope import component
from zope import interface
from zope import schema
from zope.i18n import interfaces as i18nifaces
from zope.app.intid.interfaces import IIntIds
from zope.cachedescriptors.property import Lazy
from zope import event
from zope.app.event import objectevent

from p4a.plonetagging import l10nutils
from p4a.plonetagging import utils
from p4a.plonetagging import interfaces

from Products.CMFCore import utils as cmfutils
from Products.Five.browser import BrowserView
from Products.Five.traversable import Traversable
from Products.Five.formlib import formbase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

lovelytag_dir = os.path.dirname(lovely.tag.browser.__file__)

import logging
logger = logging.getLogger('p4a.plonetagging.tagging')

class TaggingView(BrowserView):
    """View for working with tags.
    """

    def tagging_url(self):
        portal = cmfutils.getToolByName(self.context, 'portal_url') \
                 .getPortalObject()
        return portal.absolute_url() + '/tagging'

    def tag_url(self, tag):
        # urllib.quote doesn't like unicode strings
        tag = utils.escape(tag).encode('utf-8')
        return self.tagging_url() + '/tags/'+ urllib.quote(tag)

    def user_tags_url(self):
        return self.tagging_url() + '/tags-user.html'

    def alluser_tags_url(self):
        return self.tagging_url() + '/tags-alluser.html'

    @Lazy
    def engine(self):
        return component.queryUtility(ITaggingEngine)

    @Lazy
    def tagging(self):
        return ITagging(Acquisition.aq_inner(self.context))

    @Lazy
    def intids(self):
        return component.getUtility(IIntIds, context=self.engine)

    @Lazy
    def portal(self):
        return self.context.portal_url.getPortalObject()

    @Lazy
    def current_user(self):
        mtool = self.portal.portal_membership
        return mtool.getAuthenticatedMember().getUserName()

    @Lazy
    def current_item(self):
        return self.intids.getId(Acquisition.aq_inner(self.context))

    @Lazy
    def tagging_config(self):
        return component.getUtility(interfaces.ITaggingConfig)

    def _create_cloud(self, maxTags=100, calc=None, items=None, users=None):
        cloud = self.engine.getCloud(items=items, users=users)
        blacklist = self.tagging_config.tagcloud_tag_blacklist or []
        blacklist = [x.strip().lower() for x in blacklist if x.strip()]
        if blacklist:
            origcloud = cloud
            cloud = set()
            for tag, count in origcloud:
                if tag.strip().lower() not in blacklist:
                    cloud.add((tag, count))

        return lovely.tag.browser.tag.normalize(cloud, maxTags, 10, calc)

    def get_cloud(self, maxTags=100, calc=None):
        """Return a cloud for all items and all users in the system.
        """
        return self._create_cloud(maxTags, calc)

    def get_user_cloud(self, maxTags=100, calc=None):
        """Return a cloud for all items for just the current user.
        """
        return self._create_cloud(maxTags, calc, None, [self.current_user])

    def get_contextual_cloud(self, maxTags=100, calc=None):
        """Return a cloud for just the current context's tags for all users.
        """

        return self._create_cloud(maxTags, calc,
                                  [self.current_item])

    def get_contextual_user_cloud(self, maxTags=100, calc=None):
        """Return a cloud for just the current context's tags for just the
        current user.
        """

        return self._create_cloud(maxTags, calc,
                                  [self.current_item],
                                  [self.current_user])

import zope.app.form.browser.textwidgets
class TagsWidget(zope.app.form.browser.textwidgets.TextWidget):
    def getInputValue(self):
        # gotta make sure None isn't passed in as the lovely.tag
        # UserTagForm handler tries to do a .split() on it
        return super(TagsWidget, self).getInputValue() or u''

class UserTagForm(formbase.EditForm, lovely.tag.browser.tag.UserTagForm,
                  TaggingView):
    """Edit user-defined tags.
    """

    template = ViewPageTemplateFile('content-tags.pt')
    actions = lovely.tag.browser.tag.UserTagForm.actions

    form_fields = form.Fields(
        schema.TextLine(__name__='tags',
                        title=u'Tags',
                        description=u'Enter as many tags as you like, '
                                    u'separated by spaces',
                        required=False))
    form_fields['tags'].custom_widget = TagsWidget

    def update(self):
        satisfy_zope3_request(self.context, self.request)
        super(UserTagForm, self).update()
        if self.actions[self.prefix+'.actions.apply'].submitted() \
               and not self.errors:
            event.notify(objectevent.ObjectModifiedEvent(self.context))

    def setUpWidgets(self, *args, **kwargs):
        lovely.tag.browser.tag.UserTagForm.setUpWidgets(self,
                                                        *args,
                                                        **kwargs)

    @Lazy
    def tagging(self):
        return ITagging(Acquisition.aq_inner(self.context))


class TaggedItemListing(BrowserView):
    """A listing of tags."""

    template = ViewPageTemplateFile('tagged-items.pt')

    def __init__(self, context, request, tags=None):
        self.context = context
        self.request = request
        self.tags = tags or set()

    def __call__(self):
        return self.template()

    def _set_tags(self, tags):
        self._tags = set(tags)
    def _get_tags(self):
        return self._tags
    tags = property(_get_tags, _set_tags)

    def items_iter(self):
        """Return all objects who's tags are a superset of self.tags"""

        engine = component.getUtility(ITaggingEngine)
        intids = component.getUtility(IIntIds, context=engine)

        tags = self.tags

        # It seems getItems() does OR checking (ie if tags contains
        # set(['foo', 'bar']), then getItems(tags=tags) will return
        # any items that have either 'foo' or 'bar' tag.  This means
        # we have to do our own AND checks.
        for x in engine.getItems(tags=tags):
            try:
                objtags = engine.getTags(items=[x])
                if tags.issubset(objtags):
                    yield intids.getObject(x)
            except AttributeError:
                logger.exception('whoops, an intid points to an invalid '
                                 'object: %s' % str(x))

    def items(self):
        """Inefficient items retrieval that return all items in a
        complete list.  Used to support plone's batching which does
        not support iterators.
        """

        return [x for x in self.items_iter()]

    def test(self, x, tvalue, fvalue):
        if x:
            return tvalue
        return fvalue

class RootTagsView(TaggingView):
    """For retrieving information about all tags.
    """

    listing_name = u'tagged_item_listing'

    def __bobo_traverse__(self, REQUEST, name):
        """Allow tags/* mapping to work.
        """

        obj = Acquisition.aq_base(self)
        if hasattr(obj, name):
            return getattr(self, name)

        obj = component.getMultiAdapter((self.context, self.request),
                                        name=self.listing_name,
                                        interface=interface.Interface)
        if isinstance(name, str):
            name = unicode(name, 'utf-8')
        obj.tags = utils.unescape(name)

        return obj

class IRootTaggingView(interface.Interface):
    """
    """

class RootTaggingView(Acquisition.Implicit, Traversable, TaggingView):
    """View for displaying tagged items.
    """

    interface.implements(IRootTaggingView)

class Principal(object):

    def __init__(self, id):
        self.id = id

def satisfy_zope3_request(context, request):
    mtool = cmfutils.getToolByName(context, 'portal_membership')
    user = mtool.getAuthenticatedMember()
    request.principal = Principal(user.getUserName())
    request.locale = l10nutils.derive_locale(request)

class TagQueriableView(TaggingView):
    """Query the current context and globally for what tags that exist."""

    def tagging_available(self):
        return self.engine is not None

    def contextual_tags(self):
        """Return an iterable of all tags submitted for the current
        context (for all users).
        """

        return self.tagging.getTags()

    def contextual_user_tags(self, users=None):
        """Return an iterable of all tags submitted for the current
        context (for specified users -- where users defaults to just
        being the current user).
        """

        if not users:
            mtool = cmfutils.getToolByName(self.context, 'portal_membership')
            users = [mtool.getAuthenticatedMember().getUserName()]

        return self.tagging.getTags(users=users)

class CloudPortlet(BrowserView):
    """Portlet view.
    """

    @property
    def macros(self):
        return self.index.macros

