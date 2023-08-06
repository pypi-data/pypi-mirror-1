from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from csci.tweetsite import tweetsiteMessageFactory as _

#
from lib import twitter
from Products.CMFCore.utils import getToolByName
from lib import wwpLib
import time
import random

from email.Header import make_header
from email.MIMEMessage import Message
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText 

class IcontrolPanelAddSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    username = schema.TextLine(
        title=u'Owner user: new or existing',
        description=u'enter username',
        required=True,
        readonly=False,
        default=None,
        )    

    email = schema.TextLine(
        title=u'NEW USERS ONLY: User email address',
        description=u'(to send account details to)',
        required=False,
        readonly=False,
        default=None,
        )

    twitterAccount = schema.TextLine(
        title=u'Twitter accounts to add and associate',
        description=u'MUST be a valid Twitter account',
        required=False,
        readonly=False,
        default=None,
        )
    
    @interface.invariant
    def invariant_testFeed(input):
        # twitter feeds
        try:
            api = twitter.Api(username=input.twitterAccount)
            statuses = api.GetUserTimeline(input.twitterAccount) #this line sometimes gives json error
        except:
            raise interface.Invalid(_(u"Some error occurred !"))
        
        

class controlPanelAdd(formbase.PageForm):
    form_fields = form.FormFields(IcontrolPanelAddSchema)
    label = _(u'Add account')
    description = _(u'')

    @form.action('Create')
    def actionCreate(self, action, data):

        userid = wwpLib.nametoid(data['username'])
        regtool = getToolByName(self.context, 'portal_registration')
        memtool = getToolByName(self.context, 'portal_membership')
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        acl_users = getToolByName(portal, 'acl_users')

        #################
        ## Create/use user account
        
        #test if user exists
        userexists = False
        try:
            user = memtool.getMemberById(userid)
            if user is not None:
                userexists = True
        except:
            pass
        
        #create user
        if not userexists:
            email  = data['email']
            
            #construct random password
            passwd = ''
            i=0
            while i<10:
                passwd +=str(int(random.random()*9))
                i+=1
            
            #properties for user creation
            properties = {
                'username' : userid,
                'fullname' : data['username'],
                'email' : email,
            }
            #create user
            regtool.addMember(userid, passwd, properties=properties)
            
            #email the user
            mTo   = email
            mFrom = self.context.email_from_address
            
            #html email
            mSubj = 'Account Details'
            message = 'Your account has been activated:<br>=================================<br>'
            message += '<br><br>Please login using the following details<br><br>'
            message += '------------------------------------------------------------------' + '<br>'
            message += 'Username : ' + str(userid) + '<br>'
            message += 'Password : ' + str(passwd) + '<br>'
            message += '------------------------------------------------------------------' + '<br>'
            message += '<a href="' + self.context.absolute_url() + '/login_form">Click Here to Log in</a><br>'
            
            #non-html email
            message_b = 'Your account has been activated:\n=================================\n'
            message_b += '\n\nPlease login using the following details\n\n'
            message_b += '------------------------------------------------------------------' + '\n'
            message_b += 'Username : ' + str(userid) + '\n'
            message_b += 'Password : ' + str(passwd) + '\n'
            message_b += '------------------------------------------------------------------' + '\n'
            message_b += 'login page: ' +self.context.absolute_url() + '/login_form\n'
           
            #send the mail
            wwpLib.sendEmail(self.context, mTo, mFrom, mSubj, message, message_b)
            
        ####################
        ## create onlineFeed, owned by specified userid
        root_app = portal.restrictedTraverse('')
        portal = root_app
        
        #work out the path to folder
        item_path_fromroot = '/'.join(self.context.getPhysicalPath())
        app_loc = portal.restrictedTraverse(item_path_fromroot)
        feedtitle = data['twitterAccount']
        feedid    = wwpLib.nametoid(data['twitterAccount'])

        #create item (if it doesnt exist)
        if not app_loc.hasObject(feedid):
            app_loc.invokeFactory(type_name='onlineFeed', id=feedid)
        
        #grab the object
        item_checkout = item_path_fromroot +'/'+ feedid
        app_loc = portal.restrictedTraverse(str(item_checkout))
        
        #set properties 
        app_loc.setTitle(feedtitle)
        app_loc.setFeed_username(feedtitle)
        app_loc.setActive_feed(True)
        app_loc.setLastpost = str(time.time())
          
        #automatically publish the item
        workflow = getToolByName(self.context, "portal_workflow")
        review_state = workflow.getInfoFor(app_loc, 'review_state')
        if review_state != 'published':
            error=workflow.doActionFor(app_loc,'publish',comment='publised programmatically') 
        app_loc.reindexObject()

        # give user permissions to edit item
        memtool.setLocalRoles(app_loc, [userid], 'Editor', reindex=1)
        app_loc.reindexObject()
        
        
        
        


    @form.action('Cancel')
    def actionCancel(self, action, data):
        self.request.response.redirect(self.context.absolute_url() + '/')
        # Put the action handler code here 



