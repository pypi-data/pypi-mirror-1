from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.twitter import twitterMessageFactory as _

class Itwitschedule(Interface):
    """schedule of posts to make"""
    
    # -*- schema definition goes here -*-
    password = schema.TextLine(
        title=_(u"Password"), 
        required=True,
        description=_(u"Twitter passwore"),
    )

    username = schema.TextLine(
        title=_(u"Username"), 
        required=True,
        description=_(u"Twitter username to post with"),
    )

    tweetstogo = schema.List(
        title=_(u"Enter: 'Date, Time, Tweet' use new line for each entry"), 
        required=False,
        description=_(u"Enter: 'Date, Time, Tweet' use new line for each entry"),
    )

