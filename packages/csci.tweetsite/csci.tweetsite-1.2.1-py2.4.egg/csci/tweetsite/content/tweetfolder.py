"""Definition of the tweetfolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from csci.tweetsite import tweetsiteMessageFactory as _
from csci.tweetsite.interfaces import Itweetfolder
from csci.tweetsite.config import PROJECTNAME

tweetfolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

tweetfolderSchema['title'].storage = atapi.AnnotationStorage()
tweetfolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    tweetfolderSchema,
    folderish=True,
    moveDiscussion=False
)

class tweetfolder(folder.ATFolder):
    """folder contatining tweets"""
    implements(Itweetfolder)

    meta_type = "tweetfolder"
    schema = tweetfolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(tweetfolder, PROJECTNAME)
