from qi.jabberHelpdesk.kss.IJabberHelpdeskKSSCommands import IJabberHelpdeskKSSCommands
from kss.core import CommandSet
from zope import interface

class JabberHelpdeskKSSCommands(CommandSet):
	interface.implements(IJabberHelpdeskKSSCommands)
	
	def resetScrollbar(self, selector):
		command = self.commands.addCommand('resetScrollbar', selector)
	def resetInput(self, selector):
		command = self.commands.addCommand('resetInput', selector)
