from zope import component
from zope import interface
import AccessControl
from Acquisition import aq_inner
from lovely.tag import engine
from lovely.tag import tagging
from lovely.tag import interfaces
from p4a.plonetagging import interfaces as ptifaces
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import DynamicType

class ContentTaggingEngine(SimpleItem, engine.TaggingEngine):
    """A Zope2 capable persistent tagging engine.
    """

    # __parent__ returns None which trips site manager lookup, gotta force
    # the five sitemanager adapter to fall back to aq

    @property
    def __parent__(self):
        raise AttributeError()

    def getTags(self, items=None, users=None):
        # to work around a lovely.tag bug where sometimes a single user
        # is incorrectly passed in as a string
        if users is not None and not isinstance(users, (tuple, list)):
            users = [users]
        return engine.TaggingEngine.getTags(self, items, users)

class UserTagging(tagging.UserTagging):
    component.adapts(DynamicType.DynamicType)

    @property
    def _pid(self):
        return AccessControl.getSecurityManager().getUser().getId()

class TaggingConfig(SimpleItem):
    interface.implements(ptifaces.ITaggingConfig)

    def __init__(self, *args, **kwargs):
        super(TaggingConfig, self).__init__(args, kwargs)
        self.tagcloud_tag_blacklist = []

def lookup_tagging_config(context):
    return component.queryUtility(ptifaces.ITaggingConfig, context=context)

def update_keywords(obj, evt):
    engine = component.queryUtility(interfaces.ITaggingEngine)
    if engine is not None:
        # unfortunately the tagging adapter doesn't bother checking
        # to see if a tagging engine utility is available until it just
        # tries to use it
        tagging = interfaces.ITagging(aq_inner(obj), None)
        if tagging is not None:
            obj.setSubject(list(tagging.getTags()))
            obj.reindexObject()
