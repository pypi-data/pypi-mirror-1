from zope import interface
from zope import schema

class ITaggingConfig(interface.Interface):
    tagcloud_tag_blacklist = schema.List(title=u'Tag Cloud Tag Black List',
                                         description=u'Tags to ignore when '
                                                     u'generating a tag cloud',
                                         value_type=schema.TextLine())
