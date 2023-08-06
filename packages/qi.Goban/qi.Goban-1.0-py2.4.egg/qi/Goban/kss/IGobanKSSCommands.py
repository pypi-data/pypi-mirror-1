from zope import interface

class IGobanKSSCommands(interface.Interface):
	"""Livechat KSS commands
	"""

	def setInputValue(selector):
		"""
		"""