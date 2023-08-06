from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.twitter import twitterMessageFactory as _

class Itwitrss(Interface):
    """Directly merge RSS feeds to a twitter stream"""
    
    # -*- schema definition goes here -*-
    rsslist = schema.List(
        title=_(u"RSS feeds to merge"), 
        required=False,
        description=_(u"enter the url of the feeds you want to merge"),
    )

    password = schema.TextLine(
        title=_(u"Twitter Password"), 
        required=True,
        description=_(u"password"),
    )

    username = schema.TextLine(
        title=_(u"Twitter Username"), 
        required=True,
        description=_(u"username"),
    )

