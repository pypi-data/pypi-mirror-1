from zope.interface import implements
from zope import schema
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.formlib.form import Fields
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from qi.Goban import GobanMessageFactory as _


class IRecentGamesPortlet(IPortletDataProvider):
	"""A portlet which shows recently modified games.
	"""

	title = schema.TextLine(title=_(u"label_portletTitle",
								default=u"Portlet title"),
						required=True,
						default=u"Recent games")

	count = schema.Int(title=_(u"label_recentCount",
								default=u"Number of items to display"),
					   description=_(u"help_recentCount",
								default=u"How many items to list."),
					   required=True,
					   default=5)


class Assignment(base.Assignment):
	implements(IRecentGamesPortlet)

	title = u"Recent games"
	count = 5

	def __init__(self, title=None, count=None):
		if title is not None:
			self.title=title
		if count is not None:
			self.count=count


class Renderer(base.Renderer):
	def __init__(self, context, request, view, manager, data):
		base.Renderer.__init__(self, context, request, view, manager, data)

	@memoize
	def results(self):
		ct=getToolByName(self.context, "portal_catalog")
		normalize=getUtility(IIDNormalizer).normalize
		icons=getMultiAdapter((self.context, self.request),
								name="plone").icons_visible()
		if icons:
			portal=getMultiAdapter((self.context, self.request),
								name="plone_portal_state").portal_url()+"/"

		brains=ct(
				object_provides="qi.Goban.interfaces.IGoGame",
				sort_on="modified",
				sort_order="reverse",
				sort_limit=self.data.count)[:self.data.count]

		def morph(brain):

			return dict(
					title = brain.Title,
					description = brain.Description,
					url = brain.getURL(),
					icon = icons and portal+brain.getIcon or None,
					review_state = normalize(brain.review_state),
					portal_type = normalize(brain.portal_type),
					date = brain.modified)
		return [morph(brain) for brain in brains]

	@property
	def available(self):
		return len(self.results())>0

	def update(self):
		self.games=self.results()

	@property
	def title(self):
		return self.data.title

	@property
	def recent_link(self):
		state=getMultiAdapter((self.context, self.request),
								name="plone_portal_state")
		return state.portal_url()+"/@@recent_games"

	render = ViewPageTemplateFile("recent.pt")


class AddForm(base.AddForm):
	form_fields = Fields(IRecentGamesPortlet)
	label = _(u"label_addPortlet",
				default=u"Add recent games portlet.")
	description = _(u"help_addPortlet",
			default=u"This portlet shows recently modified games.")

	def create(self, data):
		return Assignment(title=data.get("title"), count=data.get("count"))


class EditForm(base.EditForm):
	form_fields = Fields(IRecentGamesPortlet)
	label = _(u"label_addPortlet",
				default=u"Add recent games portlet.")
	description = _(u"help_addPortlet",
			default=u"This portlet shows recently modified games.")

