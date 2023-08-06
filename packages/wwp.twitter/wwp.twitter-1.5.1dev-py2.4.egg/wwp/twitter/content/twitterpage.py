"""Definition of the TwitterPage content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from wwp.twitter import twitterMessageFactory as _
from wwp.twitter.interfaces import ITwitterPage
from wwp.twitter.config import PROJECTNAME

TwitterPageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'password',
        storage=atapi.AnnotationStorage(),
        widget=atapi.PasswordWidget(
            label=_(u"Password"),
            description=_(u"Password to enable posting from this site"),
        ),
        default=_(u""),
    ),


    atapi.StringField(
        'username',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Username"),
            description=_(u"Username of feed to display"),
        ),
        default=_(u""),
    ),

    atapi.IntegerField(
        'numbertodisp',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Number of posts to display"),
            description=_(u"Field description"),
        ),
        default=_(u"10"),
        validators=('isInt'),
    ),
    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

TwitterPageSchema['title'].storage = atapi.AnnotationStorage()
TwitterPageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(TwitterPageSchema, moveDiscussion=False)

class TwitterPage(base.ATCTContent):
    """Twitter Page"""
    implements(ITwitterPage)

    meta_type = "TwitterPage"
    schema = TwitterPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    password     = atapi.ATFieldProperty('password')
    username     = atapi.ATFieldProperty('username')    
    numbertodisp = atapi.ATFieldProperty('numbertodisp')



atapi.registerType(TwitterPage, PROJECTNAME)
