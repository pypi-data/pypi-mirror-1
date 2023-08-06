from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.twitter import twitterMessageFactory as _

import twitter
import find_urls
import simplejson  # http://undefined.org/python/#simplejson
import urllib
import datetime

from Products.statusmessages.interfaces import IStatusMessage



class ItwittertrendsView(Interface):
    """
    twittertrends view interface
    """

    def test():
        """ test method"""


class twittertrendsView(BrowserView):
    """
    twittertrends browser view
    """
    implements(ItwittertrendsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def twitter_trends(self):
        if hasattr(self.context, 'trends_info'):
            return self.context.trends_info
        else:
            return 'no trends posted yet'
        

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
