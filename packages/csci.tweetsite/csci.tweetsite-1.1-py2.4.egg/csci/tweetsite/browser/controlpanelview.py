from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.tweetsite import tweetsiteMessageFactory as _

#
from Products.CMFCore.utils import getToolByName

class IcontrolPanelView(Interface):
    """
    controlPanel view interface
    """

    def test():
        """ test method"""


class controlPanelView(BrowserView):
    """
    controlPanel browser view
    """
    implements(IcontrolPanelView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


        

        
    
    