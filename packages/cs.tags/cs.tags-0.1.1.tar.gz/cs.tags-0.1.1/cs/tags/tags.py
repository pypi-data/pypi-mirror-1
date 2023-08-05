import persistent
from persistent.list import PersistentList
import re

from zope.annotation import IAnnotations
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements

from cs.tags.interfaces import ITaggable, ITagged, ITagsTools

#======================================================================
class Tagged(object):
    """ """
    implements(ITagged)
    adapts(ITaggable)

    def __init__(self, context):
        """ """
        self.context = context
        annotations = IAnnotations(context)
        tags = annotations.get('tags', None)
        if tags is None:
            tags = annotations['tags'] = PersistentList()
        self._tags = tags

    def tags_fget(self):
        """ """
        return self._tags            
    def tags_fset(self,tags):
        """ """
        tagsTools = zapi.queryUtility(ITagsTools)
        for t in tagsTools.clean_the_tags(tags):
            self._tags.append(t)
        
    def tags_fdel():
        """ """
        del self._tags
    tags = property(fget=tags_fget,fset=tags_fset,fdel=tags_fdel,doc="tags")



#======================================================================
class TagsTools(object):
    """ """
    implements(ITagsTools)

    def clean_the_tags(self, tags=''):
        """ gets an string and returns a list"""

        clean_tags = []

        if tags.find('"') != -1:
           TAGS = "\"(?P<letter>[^\"]*)\""
           rx = re.compile(TAGS, re.IGNORECASE)
           for cadena in rx.findall(tags):
               tag = cadena.strip()
               if tag != '' : clean_tags.append(tag)
           tags = rx.sub('', tags)
           tags = tags.replace('\"','')

        if tags.find(',') != -1:
           TAGS = "(?P<letter>[^,]*)"
           rx = re.compile(TAGS, re.IGNORECASE)
           for cadena in rx.findall(tags):
               tag = cadena.strip()
               if tag != '' : clean_tags.append(tag)
           tags = rx.sub('', tags)
           tags = tags.replace(',','')

        if tags.find(' ') != -1:
    
           TAGS = "(?P<letter>[^ ]*)"
           rx = re.compile(TAGS, re.IGNORECASE)
           for cadena in rx.findall(tags):
               tag = cadena.strip()
               if tag != '' : clean_tags.append(tag)
           tags = rx.sub('', tags)
           tags = tags.replace(' ','')

        return clean_tags
