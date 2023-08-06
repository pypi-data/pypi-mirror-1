from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.tweetsite import tweetsiteMessageFactory as _

import urllib
import datetime
import time
import random
import unicodedata
import re
from lib import twitter
from lib import feedparser
from lib import google_short
from lib import wwpLib


# some utility functions
def _removeSymb(text):
    from string import maketrans
    illegal  = '.,!"£$%^&*()_+=[]{}@#~?/><|\'¬`;:'
    
    for ill in illegal:
        text = text.replace(ill,'')
    
    text = text.replace('<br>','')
    text = text.replace('\n','')
    
    return text
    
def _publishNews(context, title, description, text, newsSubDir,creator):
    '''publishes a news item to the site repository'''
    #####################################
    ##post and publish news item

    today = datetime.date.today()
    news_id = str(title)+ '-' +str(today)
    news_id += '-' + str(random.random()*100)[:2]
    news_id = news_id.replace(' ','-')
    news_id = _removeSymb(news_id)
    news_id = news_id.lower()

    #go to news folder
    root_app = context.restrictedTraverse(newsSubDir)
    #create item
    news_item = root_app.invokeFactory(type_name='News Item',
                                       id=news_id,
                                       title=title,
                                       description=description,
                                       text=text)
    root_app.reindexObject()
    
    #automatically publish news item
    root_app = context.restrictedTraverse(newsSubDir+'/'+news_id)
    urltool  = getToolByName(context, 'portal_url')
    workflow = getToolByName(context, "portal_workflow")
    review_state = workflow.getInfoFor(root_app, 'review_state')
    if review_state != 'published':
        error=workflow.doActionFor(root_app,'publish',comment='publised programmatically')
        
    
    #change owner
    creator = [creator]
    root_app.setCreators(creator) 
    
    
    root_app.reindexObject()

        
def _get_short(server='',
              action='get_or_create_hash',
              hmac='',
              email='',
              url='',
              short_name='anything',
              is_public='true'):    
    
    request_url = google_short.make_request_uri(server,                           #short.cannonscientific.com
                                                action,                           #get_or_create_hash
                                                hmac,                             #foobar
                                                user=email,                       #toor@cannonscientific.com
                                                url=url,                          #http://www.google.com
                                                shortcut=short_name,              #anything
                                                is_public=str(is_public).lower()  #true
                                                )

    response = urllib.urlopen(request_url)
    res = response.read()
    res = res.replace('true','True')
    res_dict = eval(res)
    end_url = 'http://' + str(server) + '/' + str(res_dict['shortcut'])
    
    return end_url
def _fix_urls(text):
    pat_url = re.compile(  r'''(?x) (((\s((http|ftp|https)://(\S*)\.)|((http|ftp|https)://))\S+\.\S+)|((\S+)\.(\S+)\.(\S+))) ''')
    pat_email = re.compile(r'''(?x) ((\S+)@(\S+)\.(\S+))''')

    for url in re.findall(pat_url, text):
        if url[0].startswith('http'):
            text = text.replace(url[0], '<a href="%(url)s">%(url)s</a>' % {"url" : url[0]})
        else:
            text = text.replace(url[0], '<a href="http://%(url)s">%(url)s</a>' % {"url" : url[0]})

    for email in re.findall(pat_email, text):
        text = your_string.replace(email[1], '<a href="mailto:%(email)s">%(email)s</a>' % {"email" : email[1]})

    return text
#

class IcontrolpanelupdateView(Interface):
    """
    controlpanelupdate view interface
    """
    #def test():
        #""" test method"""
   
class controlpanelupdateView(BrowserView):
    """
    controlpanelupdate browser view
    """
    implements(IcontrolpanelupdateView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def update_feeds(self):

        #check when each post was posted last
        if not hasattr(self.context, 'feed_lastposts'):
            self.context.feed_lastposts = {}
        
        feed_lastposts = self.context.feed_lastposts
        
        ####################################################
        ## get list of ACTIVE feeds
        #################################################### 
        index = self.context.objectValues()
        #from listed feeds, get active ones
        active_feeds = []
        for ind in index:
            if ind.portal_type == 'onlineFeed':
                active  = ind.active_feed
                feed    = ind.feed_username
                cats    = ind.categories
                
                

                #get user to post with (if more than one, top by alphabetical)
                roles = ind.get_local_roles()
                try:
                    postwith = roles[1][0]
                except:
                    postwith = 'admin'
                
                #activated by user
                if active:
                    details = [feed, cats, postwith]
                    active_feeds.append(details)

        ####################################################
        ## Grab Tweets
        ####################################################         
        #grab time of last update
        if self.context.lastpost == '':
            self.context.lastpost = str(time.mktime(datetime.datetime.utcnow().timetuple()))
        time_sec = float(self.context.lastpost)
        
        #
        api_delay = time.time() - (60*3)
        #        
        
        output = ''
        for details in active_feeds:
            feed = details[0]
            cats = details[1]
            user = details[2]
            
            output = ''
            api = twitter.Api(username=feed)
            statuses = api.GetUserTimeline(feed) #this line sometimes gives json error
            status_output = []

            #now sort out the statuses
            for s in statuses:
                
                if time_sec < s.created_at_in_seconds:
                    
                    if s.created_at_in_seconds < api_delay:

                        #check premium activated
                        premium = False
                        if feed in self.context.premiumlist:
                            premium = True
                        
                        postnow = False
                        
                        print '=========================='
                        if premium == False:
                            print feed, 'not premium'
                            # non-premium posts
                            if feed in feed_lastposts:
                                print 'old time exists',feed_lastposts[feed]
                                #check time between then and now
                                if (time.time() - float(feed_lastposts[feed])) < 500: #(60*60*24):
                                    #do not post
                                    print '--too soon', (time.time() - float(feed_lastposts[feed])), (60*60*24)
                                else:
                                    #post
                                    print '--not too soon, posting ', (time.time() - float(feed_lastposts[feed])), (60*60*24)
                                    postnow = True
                            else:
                                #it is first time, post and then update
                                postnow = True
                        else:
                            # PREMIUM posts
                            postnow = True
                        
                        if postnow:
                            self.context.feed_lastposts[feed] = str(time.time())
    
                            #activate urls
                            stext = _fix_urls(s.text)
                            #post in the desired categories
                            for cat in cats:
                                _publishNews(self.context, 
                                             title=s.text, 
                                             description='',
                                             text=stext,
                                             newsSubDir=cat,
                                             creator=user)

        ##update time of last update
        self.context.lastpost = str(api_delay) #str(time.time()) 
        self.context.reindexObject()

        return output
        
        
        
        
        
    
    
    
    
    
    
