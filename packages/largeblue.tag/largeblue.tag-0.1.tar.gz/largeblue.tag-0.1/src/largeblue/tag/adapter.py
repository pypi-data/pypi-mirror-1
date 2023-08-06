from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements

from interfaces import ITag, ITaggable

KEY = 'largeblue.tag.Tags'


class Tag(object):
    implements(ITag)
    adapts(ITaggable)
    def __init__(self, context):
        self.context = self.__parent__ = context
        annotations = IAnnotations(self.context)
        mapping = annotations.get(KEY)
        if mapping is None:
            mapping = annotations[KEY] = PersistentList([])
        self.mapping = mapping
    
    def add_tag(self, tag):
        if tag not in self.mapping:
            self.mapping.append(str(tag).encode('utf-8'))
        
    
    def remove_tag(self, tag):
        if tag in self.mapping:
            self.mapping.remove(tag)
        
    
    def update_tags(self, tags):
        # remove tags
        for tag in self.mapping:
            if tag not in tags:
                self.remove_tag(tag)
            
        
        # add new tags
        for tag in tags:
            if tag and tag not in self.mapping:
                self.add_tag(tag)
            
        
    
    @property
    def tags(self):
        return list(self.mapping)
    
    def get_tagstring(self):
        return u' '.join(self.tags)
    
    def set_tagstring(self, tagstring):
        tags = tagstring.split(u' ')
        tags = [tag.strip() for tag in tags]
        self.update_tags(tags)
    
    tagstring = property(
        get_tagstring, 
        set_tagstring
    )

