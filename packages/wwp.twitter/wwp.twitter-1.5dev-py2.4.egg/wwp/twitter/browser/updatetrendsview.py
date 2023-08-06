from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import datetime
import time
import twitter
import simplejson
import urllib
import find_urls
import sys

from Products.statusmessages.interfaces import IStatusMessage


class IupdatetrendsView(Interface):
    """
    updatetrends view interface
    """

    def test():
        """ test method"""


class updatetrendsView(BrowserView):
    """
    updatetrends browser view
    """
    implements(IupdatetrendsView)

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
    
    
    def update_trends(self):
        
        now_date = datetime.datetime.now()
        
        ##########################################
        #get the latest trends:
        raw_trends = urllib.urlopen('http://search.twitter.com/trends/current.json')

        result = simplejson.load(raw_trends)           
        trends_out = []
        for time2 in result['trends']:
            for item in result['trends'][time2]:
                trends_out.append(item['name'])
        # ---- add google link to each entry
        i=0
        trend_links = []
        while i<len(trends_out):
            trend_str = trends_out[i].replace(' ','+')
            trend_str = trend_str.replace('#','%23')
            trenditem = '<td>' + trends_out[i] + '</td><td><a href="http://www.google.com/cse?cx=partner-pub-5725171018504863%3Ali44pd-byhr&ie=ISO-8859-1&q=' + trend_str + '&sa=Search">Search Google</a></td>'
            trenditem += '<td><a href="http://twitter.com/search?q=' + trend_str + '&sa=Search">Search Twitter</a></td>'
            trend_links.append(trenditem) 
            i+=1
        # ---- save to contetnt item
        self.context.trends_info = trend_links
        
        
        
        ##########################################
        #post to twitter once a day
        today = datetime.date.today()
        today_t = str(today)+' '+'09:00'
        now_date = datetime.datetime.now()
        when_date = datetime.datetime( *time.strptime(today_t,"%Y-%m-%d %H:%M")[:5])
        
        #create last post parameter
        if not hasattr(self.context, 'lastpost'):
            self.context.lastpost = '0'
        
        print '----------------------'
        
        #check logic
        if self.context.postresults:
            
            #if not posted yet today ...
            if today != self.context.lastpost:
                
                #check time
                if now_date > when_date:
                    
                    ########################################
                    #post it on twitter
                    post_history = str(today)
                    
                    #check login details
                    if self.context.username == '':
                        IStatusMessage(self.request).addStatusMessage(_('Username not set! Cannot post'), type='error')
                    if self.context.password == '':
                        IStatusMessage(self.request).addStatusMessage(_('Password not set! Cannot post'), type='error')
                    #login to twitter
                    try:
                        api = twitter.Api(username=self.context.username, password=self.context.password)
                        post_history += ' Tlogin OK'
                    except:
                        IStatusMessage(self.request).addStatusMessage( _('Could not login to twitter'), type='error')
                        post_history += ' Tlogin FAIL'
                    #post the message
                    try:
                        #construct the post
                        twit_text = 'http://tiny.cc/MeYTX Top Tweets Today: '
                        for trend in trends_out[:5]:
                            twit_text += trend + ', '
                        statuses = api.PostUpdate(status=twit_text[:140], in_reply_to_status_id=None)
                        post_history += ' Tpost OK'
                    except:
                        IStatusMessage(self.request).addStatusMessage( _('Error posting to twitter'), type='error')
                        post_history += ' Tpost FAIL'
                        
                        
                        
                        
                        
                        
                    ########################################
                    #post the news item
                    
                    #create news item as history
                    root_app = self.context.restrictedTraverse('news')
                    news_id = 'Top tweets ' +str(today)
                    news_id = news_id.replace(' ','-')
                    news_id = news_id.replace(':','-')
                    
                    newspost_list = 'Top 10 Tweets: <table align=center><tr>' + ('</tr><tr>').join(trend_links) + '</tr></table>'
                    
                    try:
                        news_item = root_app.invokeFactory(type_name='News Item',
                                                           id=news_id,
                                                           title='Top Words on ' +str(today),
                                                           description='The most popular words on twitter are :',
                                                           text=newspost_list)
                        root_app.reindexObject()
                        post_history += ' News OK'
                    except:
                        post_history += ' News FAIL'
                    
                    #automatically publish news item
                    root_app = self.context.restrictedTraverse('news/'+news_id)
                    urltool  = getToolByName(self.context, 'portal_url')
                    workflow = getToolByName(self.context, "portal_workflow")
                    review_state = workflow.getInfoFor(root_app, 'review_state')
                    if review_state != 'published':
                        error=workflow.doActionFor(root_app,'publish',comment='publised programmatically')                    
                        
                        
                        
                        
                    ########################################                  
                    #save the posting history
                    if not hasattr(self.context, 'post_history'):
                        self.context.post_history = []
                    self.context.post_history.append(post_history)
                    
                    #update last posting date
                    self.context.lastpost = today                
                
                
                
        
        return self.context.post_history[-10:]
        

        
