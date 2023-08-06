"""Definition of the twitrss content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from wwp.twitter import twitterMessageFactory as _
from wwp.twitter.interfaces import Itwitrss
from wwp.twitter.config import PROJECTNAME



twitrssSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'username',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Username"),
            description=_(u"username"),
        ),
        required=True,
    ),
    atapi.StringField(
        'password',
        storage=atapi.AnnotationStorage(),
        widget=atapi.PasswordWidget(
            label=_(u"Twitter Password"),
            description=_(u"password"),
        ),
        required=True,
    ),
    atapi.LinesField(
        'rsslist',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"RSS feeds to merge"),
            description=_(u"enter the url of the feeds you want to merge"),
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

twitrssSchema['title'].storage = atapi.AnnotationStorage()
twitrssSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(twitrssSchema, moveDiscussion=False)

class twitrss(base.ATCTContent):
    """Directly merge RSS feeds to a twitter stream"""
    implements(Itwitrss)

    meta_type = "twitrss"
    schema = twitrssSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    rsslist = atapi.ATFieldProperty('rsslist')
    password = atapi.ATFieldProperty('password')
    username = atapi.ATFieldProperty('username')

    lastposts = {}

    
    

atapi.registerType(twitrss, PROJECTNAME)
