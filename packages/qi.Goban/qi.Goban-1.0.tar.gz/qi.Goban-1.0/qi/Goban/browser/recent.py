from Acquisition import aq_base
from DateTime.DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class RecentGamesView(BrowserView):
	"""
	"""

	__call__ = ViewPageTemplateFile('recent.pt')
	
	def __init__(self, context, request):
		BrowserView.__init__(self, context, request)
		self.portal_workflow = getToolByName(self.context, 'portal_workflow')
		self.plone_utils = getToolByName(self.context, 'plone_utils')
		self.portal_catalog = getToolByName(self.context, 'portal_catalog')
		self.portal_membership = getToolByName(self.context, 'portal_membership')

	def num_games(self):
		
		catalog = self.portal_catalog
		results = catalog(object_provides='qi.Goban.interfaces.IGoGame',
						  path='/'.join(self.context.getPhysicalPath()),)
		return len(results)

	def results(self, limit=20, offset=0):
		catalog = self.portal_catalog
		results = catalog(object_provides='qi.Goban.interfaces.IGoGame',
							sort_on='modified',
							sort_order='reverse',
							sort_limit=(offset+limit),
							path='/'.join(self.context.getPhysicalPath()))[offset:offset+limit]
		return filter(None, [self._buildDict(r.getObject()) for r in results])

	def _buildDict(self, ob):
		wfstate = self.portal_workflow.getInfoFor(ob, 'review_state')
		wfstate = self.plone_utils.normalizeString(wfstate)

		creator = ob.Creator()
		creatorInfo = self.portal_membership.getMemberInfo(creator)
		if creatorInfo is not None and creatorInfo.get('fullname', "") != "":
			creator = creatorInfo['fullname']
		return {'Title': ob.title_or_id(),
				'Description' : ob.Description(),
				'absolute_url': ob.absolute_url(),
				'review_state_normalized' : wfstate,
				'creator' : creator,
				'is_new' : self._is_new(ob.modified()),
			   	'blackPlayer': ob.getBlackPlayer(),
				'blackRating': ob.getBlackRating(),
			   	'whitePlayer': ob.getWhitePlayer(),
				'whiteRating': ob.getWhiteRating(),
				'datePlayed': ob.getDatePlayed(),
				'place': ob.getPlace(),
				'handicap':ob.getHandicap()
				}
			
	def _is_new(self, modified):
		llt = getattr(aq_base(self), '_last_login_time', [])
		if llt == []:
			m = self.portal_membership.getAuthenticatedMember()
			if m.has_role('Anonymous'):
				llt = self._last_login_time = None
			else:
				llt = self._last_login_time = m.getProperty('last_login_time', 0)
		if llt is None: # not logged in
			return False
		elif llt == 0: # never logged in before
			return True
		else:
			return (modified >= DateTime(llt))
