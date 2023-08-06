from zope import event
from zope.component import getUtility
from zope.formlib import form
from Products.Archetypes.event import ObjectEditedEvent

from Acquisition import aq_inner
from Products.Five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.form.validators import null_validator

from qi.Goban.interfaces import IAddVariation
from qi.Goban import GobanMessageFactory as _
from qi.Goban.lib.sgf2xml import *
from copy import deepcopy

class AddVariationView(formbase.PageForm):
	"""Add a new variation
	"""
	
	label = _(u"label_addVariation",default=u"Add variation")
	form_fields = form.FormFields(IAddVariation)
	
	@form.action(_(u"label_addAction",default=u"Add"))
	def action_add(self, action, data):
		"""
		"""
		context = aq_inner(self.context)

		try:
			sgfFile=data['varSgf']
			xmlConv = sgf2xml(sgfFile)
			newVarList = xmlConv.variations
			oldVarList = deepcopy(context.variations)

			# Compare moves only not comments.

			for key in newVarList.keys():
				newVarList[key] = newVarList[key][0]
			for key in oldVarList.keys():
				oldVarList[key] =oldVarList[key][0]


			newNonDupl = [varKey for varKey in newVarList.keys() if newVarList[varKey] not in oldVarList.values()]
			oldNonDupl = [varKey for varKey in oldVarList.keys() if oldVarList[varKey] not in newVarList.values()]

			if len(oldNonDupl):
				raise Exception(_(u"error_origVariationNotFound",
					default=u"One or more of the original variations were not found in the file you specified. Please download the original and just add variations withoud editing existing ones."))

			if not len(newNonDupl):
				raise Exception(_(u"error_noNewVariationFound",default=u"No new variations were found."))

		except Exception, e:
			IStatusMessage(self.request).addStatusMessage(str(e), type='error')
		else:
			# There must be a way to do this properly but can't think right now... XXX UGLY CRAP
			fileField = context.getField('sgf')
			filename = fileField.getFilename(context)
			context.setSGF(sgfFile)
			fileField.setFilename(context,filename)

			# Fire the object modified event.
			event.notify(ObjectEditedEvent(context))

			IStatusMessage(self.request).addStatusMessage(_(u"info_variationAdded",default=u"Variation(s) added."),type='info')
			self.request.response.redirect(context.absolute_url())
			return ''
			
			
	@form.action(_(u"label_cancelAction",default=u"Cancel"), validator=null_validator)
	def action_cancel(self, action, data):
		"""Cancel 
		"""
		context = aq_inner(self.context)
		
		confirm = _(u"info_variationImportCanceled",default=u"Variation import cancelled.")
		IStatusMessage(self.request).addStatusMessage(confirm, type='info')
		
		self.request.response.redirect(context.absolute_url())
		return ''
