from zope.interface import Interface
from zope.annotation.interfaces import IAnnotatable
from zope.schema import List, TextLine

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")


class ITag(Interface):
    tags = List(
        title = _(u'Tags'),
        description = _(u"List of keywords or 'tags'"),
        required = False
    )
    tagstring = TextLine(
        title = _(u'Tag String'),
        description = _(u"All tags as a ' ' seperated string"),
        required = False
    )
    def add_tag(tag):
        """Add a tag"""
    
    def remove_tag(tag):
        """Remove a tag"""
    
    def update_tags(self, tags):
        """Overwrite tags with a new list of tags"""
    


class ITaggable(IAnnotatable):
    """Marker interface"""
