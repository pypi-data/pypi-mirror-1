from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from qi.Goban.interfaces import IGoGame
from qi.Goban import GobanMessageFactory as _

class GobanViewlet(BrowserView):
	"""Viewlet that displays a goban
	"""
	
	implements(IViewlet)
	render = ViewPageTemplateFile('goban.pt')
	
	def __init__(self, context, request, view, manager):
		super(GobanViewlet, self).__init__(context, request)
		self.__parent__ = view
		self.view = view
		self.manager = manager
		self.gogame = IGoGame(self.context)
		
	def boardSize(self):
		"""
		"""
		return self.gogame.boardSize