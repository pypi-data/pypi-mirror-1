"""Definition of the onlineFeed content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from csci.tweetsite import tweetsiteMessageFactory as _
from csci.tweetsite.interfaces import IonlineFeed
from csci.tweetsite.config import PROJECTNAME

#
from Products.CMFCore.utils import getToolByName

onlineFeedSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'feed_username',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Feed Username"),
            description=_(u"enter the username of feed to manage"),
        ),
        required=True,
    ),
    
    atapi.BooleanField(
        'active_feed',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Active"),
            description=_(u"activate/deactivate feed"),
        ),
    ),
    
    atapi.LinesField(
        'categories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.InAndOutWidget(
            label=_(u"Premium Feeds"),
            description=_(u"Select Premium feeds"),
        ),
        vocabulary="getCats",
        required=True,
    ),

    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

onlineFeedSchema['title'].storage = atapi.AnnotationStorage()
onlineFeedSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(onlineFeedSchema, moveDiscussion=False)

class onlineFeed(base.ATCTContent):
    """Feed to manage"""
    
    def getCats(self):
        root = getToolByName(self, 'portal_url')
        root = root.getPortalObject()
        item_path_fromroot = '/'.join(root.getPhysicalPath())
        app_loc = self.restrictedTraverse(item_path_fromroot)
        index = app_loc.objectValues()
        #from listed feeds, get active ones
        folders = []
        for ind in index:
            if ind.portal_type == 'Folder' or ind.portal_type == 'tweetfolder':
                folders.append(ind.getId())
                    
        return folders
    
    implements(IonlineFeed)

    meta_type = "onlineFeed"
    schema = onlineFeedSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    categories = atapi.ATFieldProperty('categories')

    active_feed = atapi.ATFieldProperty('active_feed')

    feed_username = atapi.ATFieldProperty('feed_username')


atapi.registerType(onlineFeed, PROJECTNAME)
