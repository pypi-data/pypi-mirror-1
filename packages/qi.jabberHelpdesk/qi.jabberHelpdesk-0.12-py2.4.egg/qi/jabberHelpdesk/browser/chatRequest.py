from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter


from Acquisition import aq_inner
from Products.Five.formlib import formbase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.form import named_template_adapter
from plone.app.form.validators import null_validator
from plone.app.form.interfaces import IPlonePageForm

from qi.jabberHelpdesk.interfaces import IChatRequest
from qi.jabberHelpdesk import HelpdeskMessageFactory as _
from qi.jabberHelpdesk.interfaces import IMessageHandler

chatRequestFormView = named_template_adapter(ViewPageTemplateFile('chatRequest.pt'))

class ChatRequestView(formbase.PageForm):
	"""Request a chat
	"""
	implements(IPlonePageForm)
	
	label = _(u"Chat with us")
	description = _(u"Welcome to our helpdesk")

	form_name =_(u"Please fill in your details")
	form_fields = form.FormFields(IChatRequest)
	
	def __init__(self,context,request):
		ChatRequestView.label = context.title
		ChatRequestView.description = context.description
		super(ChatRequestView,self).__init__(context,request)
		self.mh = getMultiAdapter((context,request),name="helpdesk_xmlrpc")
		
	def availableAgents(self):
		if self.mh.loadBot(self.context.botJid,self.context.botPassword,self.context.persistent):
			return (len(self.mh.getAvailableAgents(self.context.botJid)),
					len(self.mh.getAliveAgents(self.context.botJid)),)
		return (0,0,0)
		
	@form.action(_(u"Submit"))
	def action_submit(self, action, data):
		"""
		"""
		
		context = aq_inner(self.context)
		name=''
		subject=''
		try:
			name = data['name']
			subject = data['subject']

		except Exception, e:
			IStatusMessage(self.request).addStatusMessage(e.error_message, type='error')
		
		try:
			if self.mh.loadBot(context.botJid,context.botPassword,context.persistent):
				if self.availableAgents():
					self.request.response.redirect('@@chatView?name=%s&subject=%s'%(name,subject))
					return ''
				else:
					IStatusMessage(self.request).addStatusMessage(_(u"No available agents."), type='error')
			else:
				IStatusMessage(self.request).addStatusMessage(_(u"Could not connect to helpdesk server"), type='error')
		except Exception,e:
			IStatusMessage(self.request).addStatusMessage(_(u"Could not connect to helpdesk server"), type='error')
			print e
	# The null_validator ensures that we can cancel the form even if some
	# required fields are not entered
	@form.action(_(u"Cancel"), validator=null_validator)
	def action_cancel(self, action, data):
		"""Cancel the subscription
		"""
		context = aq_inner(self.context)
		
		confirm = _(u"Chat request cancelled.")
		IStatusMessage(self.request).addStatusMessage(confirm, type='info')
		
		self.request.response.redirect(context.absolute_url())
		return ''