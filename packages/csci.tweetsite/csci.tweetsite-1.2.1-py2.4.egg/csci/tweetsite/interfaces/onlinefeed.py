from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.tweetsite import tweetsiteMessageFactory as _

class IonlineFeed(Interface):
    """Feed to manage"""
    
    # -*- schema definition goes here -*-

    categories = schema.List(
        title=_(u"Categories to post in"), 
        required=True,
        description=_(u"select from list"),
    )


    active_feed = schema.Bool(
        title=_(u"Active"), 
        required=False,
        description=_(u"activate/deactivate feed"),
    )

    feed_username = schema.TextLine(
        title=_(u"Feed Username"), 
        required=True,
        description=_(u"enter the username of feed to manage"),
    )

