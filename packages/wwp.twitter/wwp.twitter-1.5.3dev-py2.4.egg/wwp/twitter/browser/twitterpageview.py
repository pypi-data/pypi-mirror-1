from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import twitter
import find_urls
import simplejson  # http://undefined.org/python/#simplejson
import urllib
import datetime
import time
from datetime import timedelta
import datetime

class ItwitterpageView(Interface):
    """
    twitterpage view interface
    """

    def test():
        """ test method"""


class twitterpageView(BrowserView):
    """
    twitterpage browser view
    """
    implements(ItwitterpageView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def twitter_posts(self):
        
        #-----twitter api  stuff------
        api = twitter.Api(username=self.context.username)
        statuses = api.GetUserTimeline(self.context.username) #this line sometimes gives json error
        
        status_output = []
        
        user = api.GetUser(self.context.username)

        
        header_html = '<table><tr><td>'
        header_html +='<img src="' + str(user.profile_image_url) + '" />'
        header_html +='</td><td><h1>'+str(user.name)+'</h1>'
        header_html +='Follow us on Twitter :<a href="http://www.twitter.com/'+str(user.screen_name)+'">'+str(user.screen_name)+'</a>'
        header_html +='</td></tr></table>'
        
        status_output.append(header_html)
        
        statuses = statuses[:self.context.numbertodisp]
            
            
        ###################################################################
        ## get gmt dictionary
        #get the current gmtoffset for London:
        try:
            print '---trying---'
            gmt_page = urllib.urlopen("http://www.righthearted.com/runner.py?TZ_DATA_['London']")
            #gmt_page = urllib.urlopen("http://192.168.2.60/runner.py?TZ_DATA_['London']")
    
            gmt_page = gmt_page.readlines()

            gmt_offsets = {}
            for loc in gmt_page:
                loc = loc.replace('\n','')
                loc = loc.split('=')
                gmt_offsets[loc[0]] = int(loc[1])        

            self.context.gmt_offsets = gmt_offsets
            print '---sucess---'

        except:
            print '---failed---'
            if hasattr(self.context, 'gmt_offsets'):
                print '---got old one---'
                gmt_offsets = self.context.gmt_offsets
            else:
                print '---got new one---'
                gmt_offsets = {}
                gmt_offsets['London'] = 0
                self.context.gmt_offsets = gmt_offsets
        ##
        ###################################################################            
            
            
            

        #now sort out the statuses
        for s in statuses:
            stext = find_urls.fix_urls(s.text)
            created_time = time.gmtime(float(s.created_at_in_seconds) + float(gmt_offsets['London']))
            created_time = time.strftime('%a %d %b %y, %H:%M', created_time)
            status_output.append(stext + '<br><SMALL><sub> - ' + str(created_time) +'</sub></SMALL>')
        return status_output
           
    
    
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
