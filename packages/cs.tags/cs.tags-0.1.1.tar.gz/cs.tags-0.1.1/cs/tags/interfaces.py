from zope.annotation.interfaces import IAnnotatable
from zope.interface import Interface
from zope.schema import List, TextLine
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('kelpi')

class ITaggable(IAnnotatable):
    """ a marker interface that makes something taggable """

class ITagged(Interface):
    """ store tags in a list """

    tags = List(
        title=_(u"Tags"),
        description=_(u"Tags used as description"),
        required = False,
        value_type=TextLine(title=u"Tag")
        )

class ICloudsEngine(Interface):
    """ Cache for drawing tag clouds """

    def delete(self, item=None, user=None, tags=None):
        """ """

    def update(self, item, user, tags):
        """ """

    def getRelatedTags(self, tag, n=40):
        """ """
        
    def getRelatedItems(self, item, n=40):
        """ """
        
    def getRelatedUsers(self, user, n=40):
        """ """

    def getCloud(self, items=None, users=None, n=40):
        """ """
                

class ITagsTools(Interface):

    def clean_the_tags(self, tags=''):
        """ filter the string tags and returns a list of cleaned tags """

