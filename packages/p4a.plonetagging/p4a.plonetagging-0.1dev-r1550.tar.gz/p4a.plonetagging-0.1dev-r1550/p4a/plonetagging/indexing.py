from Acquisition import aq_inner
from lovely.tag import interfaces
from zope.component.interfaces import ComponentLookupError
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

def tags(object, portal, **kwargs):
    """Return the list of tags for a particular object.
    """

    try:
        tagging = interfaces.ITagging(aq_inner(object), None)
        if tagging is None:
            raise AttributeError('Could not look up ITagging adapter')
        return list(tagging.getTags())
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('tags', tags)
