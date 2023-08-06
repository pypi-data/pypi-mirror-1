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

	def getMember(self):
		"""
		"""
		self.membership = getToolByName(self.context, 'portal_membership')
		if not self.membership.isAnonymousUser():
			minfo = self.membership.getMemberInfo()
			return minfo['fullname'] or self.membership.getAuthenticatedMember()
		return None
	
	