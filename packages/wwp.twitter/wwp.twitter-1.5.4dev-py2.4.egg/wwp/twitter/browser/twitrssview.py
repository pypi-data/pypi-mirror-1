from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import urllib
import feedparser # from http://www.feedparser.org/
import twitter
from Products.statusmessages.interfaces import IStatusMessage
import sys

class ItwitrssView(Interface):
    """
    twitrss view interface
    """

    def test():
        """ test method"""


class twitrssView(BrowserView):
    """
    twitrss browser view
    """
    implements(ItwitrssView)

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

    
    
    
    
    
    def post_twitter(self):
        
#        print self.context.lastpost
        
        if not hasattr(self.context,'lastpost'):
            self.context.lastpost = {}
        
        feedstopost = []        
        
        for feed in self.context.rsslist:
            print '---------------------------------------------'
            print feed
            
            d = feedparser.parse(feed)
            
            #if there is no previous posting record, only post last post
            if feed not in self.context.lastpost.keys():
                print '--- new feed, posting last post'
                
                #add to post of posts to add
                feedstopost.append(d['entries'][0]['title'][:140])
                
                #record the posting date
                self.context.lastpost[feed] = d['entries'][0]['title']
                
            #if history exists: post everything up to the last post recorded
            else:
                #loop over all posts in feed
                print '--------------------------------------',self.context.lastpost[feed]
                
                i=0
                while i< len(d['entries']):
                    
                    print i, d['entries'][i]['title'][:20],' --- ', self.context.lastpost[feed][:20],
                    
                    if d['entries'][i]['title'] == self.context.lastpost[feed]:
                        print '--stops here'
                        break
                    else:               
                        print '---posting : ', d['entries'][i]['title'][:20]
                        
                        #add to post of posts to add
                        feedstopost.append(d['entries'][i]['title'][:140])
                        
                    i+=1
                
                #use the newest point as new reference
                self.context.lastpost[feed] = d['entries'][0]['title']
                print '------------------------------'
                
                
                
        print '---number to post : ',len(feedstopost)
        
        history_text = 'No. posts  to .. post : ' +str(len(feedstopost))
        #login to twitter
        try:
            api = twitter.Api(username=self.context.username, password=self.context.password)
            history_text += ' - login OK -'
        except:
            IStatusMessage(self.request).addStatusMessage( _('Could not login to twitter', sys.exc_info()[0]), type='error')
            #on Failure, add to history
            history_text += ' - FAILED @ login -'
                
                
        #post the message
        try:
            for post in feedstopost:
                statuses = api.PostUpdate(status=post[:140], in_reply_to_status_id=None)
            #on sucess, add to history
            history_text += ' - Posting OK -'
        except:
            IStatusMessage(self.request).addStatusMessage( _('Error posting to twitter', sys.exc_info()[0]), type='error')
            #on Failure, add to history
            history_text += ' - FAILED @ Posting -'
        
            
        return history_text

    
    
    