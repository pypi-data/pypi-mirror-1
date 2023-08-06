from Acquisition import aq_inner

from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope.component import getUtility

from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from qi.jabberHelpdesk import HelpdeskMessageFactory as _
from qi.jabberHelpdesk.interfaces import IHelpdesk
from Products.Archetypes.atapi import DisplayList

from qi.jabberHelpdesk.interfaces import IMessageHandler

class IHelpdeskPortlet(IPortletDataProvider):
	"""
	"""
	targetHelpdesk = schema.List(title=_(u"Target helpdesk"),
			description=_(u"Link to the helpdesk of your choice"),
			required=True,
			min_length=1,
			max_length=1,
			value_type=schema.Choice(
				source=SearchableTextSourceBinder({'object_provides' : IHelpdesk.__identifier__},default_query='path:'))
			)

class Assignment(base.Assignment):
	"""
	"""
	
	implements(IHelpdeskPortlet)
	def __init__(self,targetHelpdesk=''):
		self.targetHelpdesk = targetHelpdesk

	#@property
	def title(self):
		return _(u"Helpdesk portlet")

class Renderer(base.Renderer):

	render = ViewPageTemplateFile('helpdeskPortlet.pt')

	def __init__(self, context, request, view, manager, data):
		"""
		"""
		self.context = context
		self.request = request
		self.data = data
		self.helpdesk = self._getHelpdeskFromPath(self.data.targetHelpdesk[0])
		self.mh = getUtility(IMessageHandler)		
		
		pm = getToolByName(self.context,'portal_membership')
		member = pm.getAuthenticatedMember()
		self.permissionGrant =	member.has_permission('qi.jabberHelpdesk: Use helpdesk',self.context) 

	@property
	def availableAgents(self):
		if self.mh.loadBot(self.helpdesk.botJid,self.helpdesk.botPassword,self.helpdesk.persistent):
			return len(self.mh.getAvailableAgents(self.helpdesk.botJid))
		return 0
	
	@property
	def available(self):
		"""
		"""
		return self.permissionGrant and self.availableAgents
	
	@property	
	def helpdeskLink(self):
		"""
		"""
		return self.helpdesk.absolute_url()
		
	def _getHelpdeskFromPath(self,path):
		""" gets the ad the path is pointing to"""
		if path.startswith('/'):
			path = path[1:]
		if not path:
			return None
		portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
		portal = portal_state.portal()
		return portal.unrestrictedTraverse(path, default=None)

class AddForm(base.AddForm):
	form_fields = form.Fields(IHelpdeskPortlet)
	form_fields['targetHelpdesk'].custom_widget = UberMultiSelectionWidget
	
	label = _(u"Add helpdesk portlet")
	description = _(u"This portlet lets people ask for online support from the helpdesk.")

	def create(self,data):
		return Assignment(**data)

class EditForm(base.EditForm):
	form_fields = form.Fields(IHelpdeskPortlet)
	form_fields['targetHelpdesk'].custom_widget = UberMultiSelectionWidget
	label = _(u"Edit helpdesk portlet")
	description = _(u"This portlet lets people ask for online support from the helpdesk.")