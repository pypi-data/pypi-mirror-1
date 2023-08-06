from zope.component import getUtility
from Products.CMFCore.utils import getToolByName 
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from qi.jabberHelpdesk import HelpdeskMessageFactory as _


class ChatView(BrowserView):
	"""
	"""
	__call__ = ViewPageTemplateFile('chat.pt')

	def botJid(self):
		"""
		"""
		return self.context.botJid

	def render(self):
		"""Simply return the template
		"""
		return self.template()

	
	