from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.tweetsite import tweetsiteMessageFactory as _

class Itweetfolder(Interface):
    """folder contatining tweets"""
    
    # -*- schema definition goes here -*-
