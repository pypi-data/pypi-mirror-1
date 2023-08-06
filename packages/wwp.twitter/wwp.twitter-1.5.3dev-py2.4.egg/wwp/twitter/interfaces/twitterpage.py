from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.twitter import twitterMessageFactory as _

class ITwitterPage(Interface):
    """Twitter Page"""
    
    # -*- schema definition goes here -*-
    numbertodisp = schema.Int(
        title=_(u"Number of posts to display"), 
        required=False,
        description=_(u"Field description"),
    )

    password = schema.TextLine(
        title=_(u"Password"), 
        required=False,
        description=_(u"G"),
    )

    username = schema.TextLine(
        title=_(u"Twitter Username"), 
        required=False,
        description=_(u"Username of feed to display"),
    )

