"""Definition of the twittertrends content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from wwp.twitter import twitterMessageFactory as _
from wwp.twitter.interfaces import Itwittertrends
from wwp.twitter.config import PROJECTNAME

twittertrendsSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-    
    atapi.StringField(
        'trendtype',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Type of Twitter Trend"),
            description=_(u"Make your selection"),
        ),
        required=True,
        vocabulary=['Current','Daily','Weekly'],
    ),
    

    atapi.BooleanField(
        'postresults',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Post results to feed?"),
            description=_(u"enter feed username"),
        ),
    ),

    atapi.StringField(
        'username',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Username"),
            description=_(u"Enter username to post tweets in (Optional)"),
        ),
    ),
    
    atapi.StringField(
        'password',
        storage=atapi.AnnotationStorage(),
        widget=atapi.PasswordWidget(
            label=_(u"Password"),
            description=_(u"of twitter feed (Optional)"),
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

twittertrendsSchema['title'].storage = atapi.AnnotationStorage()
twittertrendsSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(twittertrendsSchema, moveDiscussion=False)

class twittertrends(base.ATCTContent):
    """Display top words from twitter"""
    implements(Itwittertrends)

    meta_type = "twittertrends"
    schema = twittertrendsSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    password = atapi.ATFieldProperty('password')

    username = atapi.ATFieldProperty('username')

    postresults = atapi.ATFieldProperty('postresults')

    trendtype = atapi.ATFieldProperty('trendtype')
    
    lastupdate = []


atapi.registerType(twittertrends, PROJECTNAME)
