from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.twitter import twitterMessageFactory as _

class Itwittertrends(Interface):
    """Display top words from twitter"""
    
    # -*- schema definition goes here -*-
    password = schema.TextLine(
        title=_(u"Password"), 
        required=False,
        description=_(u"of twitter feed (Optional)"),
    )

    username = schema.TextLine(
        title=_(u"Username"), 
        required=False,
        description=_(u"Enter username to post tweets in (Optional)"),
    )

    postresults = schema.Bool(
        title=_(u"Post results to feed?"), 
        required=False,
        description=_(u"enter feed username"),
    )
    
    debugmode = schema.Bool(
        title=_(u"Debug Mode"), 
        required=False,
        description=_(u"posts every refresh"),
    )

    trendtype = schema.TextLine(
        title=_(u"Type of Twitter Trend"), 
        required=True,
        description=_(u"Make your selection"),
    )

