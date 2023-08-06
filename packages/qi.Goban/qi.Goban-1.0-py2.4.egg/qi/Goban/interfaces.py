from zope.interface import Interface
from zope.app.container.constraints import contains
from zope import schema

from qi.Goban import GobanMessageFactory as _
								
class IGoGame(Interface):
	"""
	"""
	
	blackPlayer = schema.TextLine(title=_(u"label_blackPlayer",default=u"Black"))
	blackRating = schema.TextLine(title=_(u"label_blackRating",default=u"Black rating"))
	whitePlayer = schema.TextLine(title=_(u"label_whitePlayer",default=u"White"))
	whiteRating = schema.TextLine(title=_(u"label_whiteRating",default=u"White rating"))
	komi = schema.Float(title=_(u"label_komi",default=u"Komi"),
						default=0.5,
						required=True)
	handicap = schema.Int(title=_(u"label_handicap",default=u"Handicap"),
						default=0,
						min=0,
						required=True)	
	event = schema.TextLine(title=_(u"label_event",default=u"Event"))
	place = schema.TextLine(title=_(u"label_place",default=u"Place"))
	round = schema.TextLine(title=_(u"label_round",default=u"Round"))
	datePlayed = schema.Date(title=_(u"label_datePlayed",default=u"Date played"))
	dateFinished = schema.Date(title=_(u"label_dateFinished",default=u"Date finished"))
	result = schema.TextLine(title=_(u"label_result",default=u"Result"))

class IPDFDiagram(Interface):
	"""
	"""
	
	movesPerDiagram = schema.Int(title=_(u"label_movesPerDiagram",default=u"Moves per diagram"),
							description=_(u"help_movesPerDiagram",default=u"The number of moves displayed in each of the diagrams."),
							required=True,
							default=50,
							min=10)
	ignoreVariations = schema.Bool(title=_(u"label_ignoreVariations",default=u"Ignore variations"),
							description=_(u"help_ignoreVariations",default=u"Check here if you don't want variations to be included."),
							default=False)
	ignoreLetters = schema.Bool(title=_(u"label_ignoreLetters",default=u"Ignore letters"),
							description=_(u"help_ignoreLetters",default=u"Check here if you don't want letter markings to be printed."),
							default=False)
	ignoreMarks = schema.Bool(title=_(u"label_ignoreMarks",default=u"Ignore marks"),
							description=_(u"help_ignoreMarks",default=u"Check here if you don't want marks to be printed."),
							default=False)

class IAddVariation(Interface):
	"""
	"""
	
	varSgf = schema.Bytes(title=_(u"label_sgf",default=u"Sgf"),
						description=_(u"help_variationSgf",default=u"the sgf file containing the new variation(s)"),
						required=True)
						