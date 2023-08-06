from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.tweetsite import tweetsiteMessageFactory as _

import datetime
import time
import re


class ItweetfolderView(Interface):
    """
    tweetfolder view interface
    """

    def test():
        """ test method"""
    def sort_content():
        ''' sort folder contents '''


class tweetfolderView(BrowserView):
    """
    tweetfolder browser view
    """
    implements(ItweetfolderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
    
    def next(self):
        if hasattr(self.request, 'page'):
            self.context.page += 1
            print self.context.page



    def sort_content(self, objects):
        
        obj_list = []
        for obj in objects:
            created_dt = str(obj.creation_date)[:19]
            created_dt = time.strptime(created_dt, '%Y/%m/%d %H:%M:%S')
            created_time = time.gmtime(float(time.mktime(created_dt)))
            created_time = time.strftime('%Y/%m/%d %H:%M', created_time)            
            obj_list.append( (created_time, obj) )
        obj_list.sort(reverse=True)

        #sort list
        return obj_list
    
    
    def fix_urls(self, text):
        pat_url = re.compile(  r'''(?x) (((\s((http|ftp|https)://(\S*)\.)|((http|ftp|https)://))\S+\.\S+)|((\S+)\.(\S+)\.(\S+))) ''')
        pat_email = re.compile(r'''(?x) ((\S+)@(\S+)\.(\S+))''')
        pat_hash = re.compile( '''((?P<hashtag>#.+?)\s)''')

        #find urls
        for url in re.findall(pat_url, text):
            good = url[0].strip()
            if good.startswith('http'):
                text = text.replace(good, '<a target="_blank" href="%(url)s">%(url)s</a>' % {"url" : good})
            else:
                text = text.replace(good, '<a target="_blank" href="http://%(url)s">%(url)s</a>' % {"url" : good})
    
        # find email addresses
        for email in re.findall(pat_email, text):
            text = text.replace(email[1], '<a target="_blank" href="mailto:%(email)s">%(email)s</a>' % {"email" : email[1]})

        #find hashtags
        text = pat_hash.sub('<a target="_blank" href="http://twitter.com/#search?q=\g<hashtag>">\g<hashtag></a> ', text)
        
        return text
        
        
        
        
        
        
        
        
        
        
        
    