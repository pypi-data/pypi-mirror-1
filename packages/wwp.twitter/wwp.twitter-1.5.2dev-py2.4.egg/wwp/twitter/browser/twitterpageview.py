from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import twitter
import find_urls
import simplejson  # http://undefined.org/python/#simplejson
import urllib
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
        
        for s in statuses:
            stext = find_urls.fix_urls(s.text)
            status_output.append(stext + '<br><SMALL><sub> - ' + s.created_at[:18] +'</sub></SMALL>')
        return status_output
           
    
    
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
