from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from wwp.twitter import twitterMessageFactory as _

import twitter
from plone.app.form.validators import null_validator
from Products.statusmessages.interfaces import IStatusMessage

class IaddtweetSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    tweettext = schema.Text(
        title=u'Enter tweet to post',
        description=u'Max 140 characters',
        required=True,
        readonly=False,
        default=None,
        )

    @interface.invariant
    def invariant_checklength(input):
        pass
	# Check input values example:
	if len(input.tweettext) > 140:
	    raise interface.Invalid(u"Set either title or subtitle.")
	
	
class addtweet(formbase.PageForm):
    form_fields = form.FormFields(IaddtweetSchema)
    label = _(u'Add Tweet')
    description = _(u'Add tweet to twitter')

    @form.action('Submit')
    def actionSubmit(self, action, data):
	#check for password
	if self.context.password =='':
	    IStatusMessage(self.request).addStatusMessage(_('Password not set! Cannot post'), type='error')
	    return
	#login to twitter
	api = twitter.Api(username=self.context.username, password=self.context.password)
	
	#post the message
	statuses = api.PostUpdate(status=data['tweettext'], in_reply_to_status_id=None)
	
	#return to view the item
	self.request.response.redirect(self.context.absolute_url() + '/')

    @form.action('Cancel', validator=null_validator)
    def actionCancel(self, action, data):
	self.request.response.redirect(self.context.absolute_url() + '/')
        # Put the action handler code here 



