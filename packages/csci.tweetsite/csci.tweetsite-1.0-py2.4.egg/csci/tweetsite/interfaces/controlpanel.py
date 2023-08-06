from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.tweetsite import tweetsiteMessageFactory as _

class IcontrolPanel(Interface):
    """create and manage user accounts"""
    
    # -*- schema definition goes here -*-

    lastpost = schema.TextLine(
        title=_(u"Last update"), 
        required=False,
        description=_(u"Time of last update"),
    )

    premiumlist = schema.List(
        title=_(u"Premium Feeds"), 
        required=False,
        description=_(u"Select Premium feeds"),
    )

