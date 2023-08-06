from qi.Goban.kss.IGobanKSSCommands import IGobanKSSCommands
from kss.core import CommandSet
from zope import interface

class GobanKSSCommands(CommandSet):
	interface.implements(IGobanKSSCommands)
	
	def setInputValue(self, selector,value):
		self.commands.addCommand('setInputValue', selector,newValue=value)
