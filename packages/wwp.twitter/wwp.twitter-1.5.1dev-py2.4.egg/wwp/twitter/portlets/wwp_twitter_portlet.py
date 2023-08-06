from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from wwp.twitter.portlets import wwp_twitter_portletMessageFactory as _
from plone.memoize.instance import memoize

import twitter

class Iwwp_twitter_portlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)

    Title = schema.TextLine(title=_(u"Portlet Title"),
                                 description=_(u"Enter the title of the portlet"),
                                 required=True)
    Feed_name = schema.TextLine(title=_(u"Twitter Username"),
                                 description=_(u"Enter the username of the twitter feed to display"),
                                 required=True)
    No_tweets = schema.TextLine(title=_(u"Number of tweets to display"),
                                 description=_(u"Enter the number of tweets to display"),
                                 required=True)
    

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(Iwwp_twitter_portlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    
    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field

    def __init__(self, Title="",
                       Feed_name="",
                       No_tweets=5):
        self.Title = Title
        self.Feed_name = Feed_name
        self.No_tweets = No_tweets

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "WWP Twitter Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('wwp_twitter_portlet.pt')
    
    @memoize
    def title(self):
        return self.data.Title
    
    @memoize
    def username(self):
        return self.data.Feed_name
    
    @memoize
    def get_tweets(self):
        username = self.data.Feed_name
        limit = int(self.data.No_tweets)
        twapi = twitter.Api()
        return twapi.GetUserTimeline(username)[:limit]
    
    


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(Iwwp_twitter_portlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(Iwwp_twitter_portlet)
