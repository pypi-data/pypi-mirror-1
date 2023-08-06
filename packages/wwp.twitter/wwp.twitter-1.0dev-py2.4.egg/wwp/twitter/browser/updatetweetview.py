from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import datetime
import time
import twitter
import find_urls
import simplejson  # http://undefined.org/python/#simplejson
import urllib
import random

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
    
    
    
    def twitter_trends(self):
        
        today = datetime.datetime.now()
        self.context.lastupdate.append(today)
        
        raw_trends = urllib.urlopen('http://search.twitter.com/trends/current.json')

        result = simplejson.load(raw_trends)            
        trends_out = []
        for time in result['trends']:
            for item in result['trends'][time]:
                trends_out.append(item['name'])

        # add google link to each entry
        i=0
        trend_links = []
        while i<len(trends_out):
            trend_str = trends_out[i].replace(' ','+')
            trend_str = trend_str.replace('#','%23')
            trenditem = '<td>' + trends_out[i] + '</td><td><a href="http://www.google.com/cse?cx=partner-pub-5725171018504863%3Ali44pd-byhr&ie=ISO-8859-1&q=' + trend_str + '&sa=Search">Search Google</a></td>'
            trenditem += '<td><a href="http://twitter.com/search?q=' + trend_str + '&sa=Search">Search Twitter</a></td>'
            trend_links.append(trenditem)  
            i+=1
        #save to contetnt item
        self.context.trends_info = trend_links		

        #post on twitter!
        if self.context.postresults:
            string_list = "http://tiny.cc/MeYTX Top Tweets Today: " + (', ').join(trends_out[:5])
            #if self.context.username == '':
                #IStatusMessage(self.request).addStatusMessage(_('Username not set! Cannot post'), type='error')
            #if self.context.password == '':
                #IStatusMessage(self.request).addStatusMessage(_('password not set! Cannot post'), type='error')
            
            #login to twitter
            api = twitter.Api(username=self.context.username, password=self.context.password)
            #post the message
            statuses = api.PostUpdate(status=string_list[:140], in_reply_to_status_id=None)
                    
            #create news item as history
            root_app = self.context.restrictedTraverse('news')
                    
            news_id = 'Top tweets ' +str(today)
            news_id = news_id.replace(' ','-')
            news_id = news_id.replace(':','-')

            newspost_list = 'Top 10 Tweets: <table align=center><tr>' + ('</tr><tr>').join(trend_links) + '</tr></table>'

            news_item = root_app.invokeFactory(type_name='News Item', 
                                               id=news_id, 
                                               title='Top Words on ' +str(today), 
                                               description='The most popular words on twitter are :',
                                               text=newspost_list)
            root_app.reindexObject()

            #automatically publish news item
            root_app = self.context.restrictedTraverse('news/'+news_id)
            urltool  = getToolByName(self.context, 'portal_url')
            workflow = getToolByName(self.context, "portal_workflow")
            review_state = workflow.getInfoFor(root_app, 'review_state')
            if review_state != 'published':
                error=workflow.doActionFor(root_app,'publish',comment='publised programmatically')

        


        return self.context.trends_info
