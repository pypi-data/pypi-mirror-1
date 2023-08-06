"""Definition of the twitschedule content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from wwp.twitter import twitterMessageFactory as _
from wwp.twitter.interfaces import Itwitschedule
from wwp.twitter.config import PROJECTNAME

twitscheduleSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'username',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Username"),
            description=_(u"Twitter username to post with"),
        ),
        required=True,
    ),

    atapi.StringField(
        'password',
        storage=atapi.AnnotationStorage(),
        widget=atapi.PasswordWidget(
            label=_(u"Password"),
            description=_(u"Twitter password"),
        ),
        required=True,
    ),

    atapi.LinesField(
        'tweetstogo',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Posts to schedule"),
            description=_(u"Enter: Date, Time, Tweet use new line for each entry"),
            rows=20,
            columns=30,
        ),
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

twitscheduleSchema['title'].storage = atapi.AnnotationStorage()
twitscheduleSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    twitscheduleSchema,
    folderish=True,
    moveDiscussion=False
)

class twitschedule(folder.ATFolder):
    """schedule of posts to make"""
    implements(Itwitschedule)

    meta_type = "twitschedule"
    schema = twitscheduleSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    password = atapi.ATFieldProperty('password')

    username = atapi.ATFieldProperty('username')

    tweetstogo = atapi.ATFieldProperty('tweetstogo')


atapi.registerType(twitschedule, PROJECTNAME)
