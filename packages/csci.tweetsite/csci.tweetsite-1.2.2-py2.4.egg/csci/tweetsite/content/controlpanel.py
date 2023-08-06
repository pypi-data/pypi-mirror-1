"""Definition of the controlPanel content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from csci.tweetsite import tweetsiteMessageFactory as _
from csci.tweetsite.interfaces import IcontrolPanel
from csci.tweetsite.config import PROJECTNAME


#
from zope.schema.vocabulary import SimpleVocabulary
from Acquisition import aq_parent





controlPanelSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'lastpost',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Last update"),
            description=_(u"Time of last update"),
        ),
    ),

    atapi.LinesField(
        'premiumlist',
        storage=atapi.AnnotationStorage(),
        widget=atapi.InAndOutWidget(
            label=_(u"Premium Feeds"),
            description=_(u"Select Premium feeds"),
        ),
        vocabulary="getVocabularyForDomains",
    ),
    
    atapi.IntegerField(
        'delay',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Delay between posts (seconds)"),
            description=_(u"(for non-premium feeds, in seconds)"),
        ),
        required=True,
        default=_(u"86400"),
        validators=('isInt'),
    ),
))



# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

controlPanelSchema['title'].storage = atapi.AnnotationStorage()
controlPanelSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    controlPanelSchema,
    folderish=True,
    moveDiscussion=False
)

class controlPanel(folder.ATFolder):
    """create and manage user accounts"""
    
    def getVocabularyForDomains(self):
        index = self.objectValues()
        
        #from listed feeds, get active ones
        all_feeds = []
        for ind in index:
            if ind.portal_type == 'onlineFeed':
                feed    = ind.feed_username
                all_feeds.append(feed)
                    
        return all_feeds
    
    implements(IcontrolPanel)

    meta_type = "controlPanel"
    schema = controlPanelSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    delay = atapi.ATFieldProperty('delay')


    lastpost = atapi.ATFieldProperty('lastpost')

    premiumlist = atapi.ATFieldProperty('premiumlist')


atapi.registerType(controlPanel, PROJECTNAME)
