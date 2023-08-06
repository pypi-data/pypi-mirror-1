from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

from Products.statusmessages.interfaces import IStatusMessage

import datetime
import time
import twitter
import find_urls
import simplejson  # http://undefined.org/python/#simplejson
import urllib
import random
import sys

class IupdatetweetView(Interface):
    """
    updatetweet view interface
    """

    def test():
        """ test method"""


class updatetweetView(BrowserView):
    """
    updatetweet browser view
    """
    implements(IupdatetweetView)

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
    
    
    
    def post_scheduled(self):
        
        now_date = datetime.datetime.now()
        
        print '---checking for posts---', now_date

        for post in self.context.tweetstogo:
            post_list = post.split(',')
            if len(post_list)>3:
                IStatusMessage(self.request).addStatusMessage(_('Badly formatted Tweet',len(post_list)), type='error')
            twit_date = post_list[0]
            twit_time = post_list[1]
            twit_text = post_list[2]

            #get posting date and time:
            try:
                when_date = datetime.datetime(*time.strptime(twit_date+twit_time, "%d/%m/%Y %H:%M")[:5])
            except:
                IStatusMessage(self.request).addStatusMessage( _('Badly formatted time and date',twit_date+twit_time, sys.exc_info()[0]), type='error')
                #on Failure, add to history
                history_text = str(now_date)+' - FAILED @ Formatting -'+str(post)
                try:
                    self.context.posted_list.append(history_text)
                except:
                    self.context.posted_list = [history_text]


            if now_date >= when_date:
                    
                    #post on twitter!
                    if self.context.username == '':
                        IStatusMessage(self.request).addStatusMessage(_('Username not set! Cannot post'), type='error')
                    if self.context.password == '':
                        IStatusMessage(self.request).addStatusMessage(_('Password not set! Cannot post'), type='error')
                    
                    #login to twitter
                    try:
                        api = twitter.Api(username=self.context.username, password=self.context.password)
                    except:
                        IStatusMessage(self.request).addStatusMessage( _('Could not login to twitter', sys.exc_info()[0]), type='error')
                        #on Failure, add to history
                        history_text = str(now_date)+' - FAILED @ login -'+str(post)
                        try:
                            self.context.posted_list.append(history_text)
                        except:
                            self.context.posted_list = [history_text]

                        
                        
                    #post the message
                    try:
                        statuses = api.PostUpdate(status=twit_text[:140], in_reply_to_status_id=None)
                        #on sucess, add to history
                        history_text = str(now_date)+' - '+str(post)
                        try:
                            self.context.posted_list.append(history_text)
                        except:
                            self.context.posted_list = [history_text]
                        
                        #remove the posted entry from list
                        tweetstogo_out = ()
                        for item in self.context.tweetstogo:
                            if item != post:
                                tweetstogo_out += (item,)
                        self.context.tweetstogo = tweetstogo_out
                    except:
                        IStatusMessage(self.request).addStatusMessage( _('Error posting to twitter', sys.exc_info()[0]), type='error')
                        #on Failure, add to history
                        history_text = str(now_date)+' - FAILED @ Posting -'+str(post)
                        try:
                            self.context.posted_list.append(history_text)
                        except:
                            self.context.posted_list = [history_text]

                    
                    
                    


        return self.context.posted_list[-10:]
