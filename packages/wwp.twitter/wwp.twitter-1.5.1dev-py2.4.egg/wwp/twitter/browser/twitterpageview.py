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
            statuses = api.GetUserTimeline(self.context.username)
            
            statuses = statuses[:self.context.numbertodisp]
            status_output = []
            
            for s in statuses:
                s = find_urls.fix_urls(s.text)
                status_output.append(s)
            return status_output
            #-----/twitter api  stuff------
            
    
    
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
