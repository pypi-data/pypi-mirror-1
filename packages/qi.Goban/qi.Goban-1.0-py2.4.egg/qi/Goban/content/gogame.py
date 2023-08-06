# -*- coding: utf-8 -*-
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, ATContentTypeSchema
from Products.ATContentTypes.content.base import ATCTContent
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from qi.Goban.interfaces import IGoGame
from qi.Goban.config import *
from qi.Goban.lib.sgflib import *
from qi.Goban.lib.Board import *
from qi.Goban.lib.Variation import *
from qi.Goban.lib.sgf2xml import *
from qi.Goban import GobanMessageFactory as _

from elementtree import ElementTree as ET
from DateTime import *
import re

GoGame_schema = ATContentTypeSchema.copy() + atapi.Schema((
	atapi.FileField('sgf',
		mutator="setSGF",
		widget=atapi.FileWidget(
			label=_(u"label_sgf",default=u"Sgf"),
		),
		required=True,
		storage=atapi.AttributeStorage()
	),
	atapi.StringField('blackPlayer',
		widget=atapi.StringWidget(
			label=_(u"label_blackPlayer",default=u"Black"),
			visible=False,
		),
		searchable=True,
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('blackRating',
		widget=atapi.StringWidget(
			label=_(u"label_blackRating",default=u"Black rating"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('whitePlayer',
		widget=atapi.StringWidget(
			label=_(u"label_whitePlayer",default=u"White"),
			visible=False,
		),
		searchable=True,
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('whiteRating',
		widget=atapi.StringWidget(
			label=_(u"label_whiteRating",default=u"White rating"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('komi',
		widget=atapi.StringWidget(
			label=_(u"label_komi",default=u"Komi"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.IntegerField(
		name='handicap',
		widget=atapi.IntegerField._properties['widget'](
			label=_(u"label_handicap",default=u"Handicap"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('event',
		widget=atapi.StringWidget(
			label=_(u"label_event",default=u"Event"),
			visible=False,
		),
		searchable=True,
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('place',
		widget=atapi.StringWidget(
			label=_(u"label_place",default=u"Place"),
			visible=False,
		),
		searchable=True,
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField('round',
		widget=atapi.StringWidget(
			label=_(u"label_round",default=u"Round"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.DateTimeField('datePlayed',
		widget=atapi.CalendarWidget(
			label=_(u"label_datePlayed",default=u"Date played"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.DateTimeField('dateFinished',
		widget=atapi.CalendarWidget(
			label=_(u"label_dateFinished",default=u"Date finished"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
	atapi.StringField(
		name='result',
		widget=atapi.StringWidget(
			label=_(u"label_result",default=u"Result"),
			visible=False,
		),
		storage=atapi.AnnotationStorage()
	),
))

GoGame_schema['title'].storage = atapi.AnnotationStorage()
GoGame_schema['description'].storage = atapi.AnnotationStorage()


finalizeATCTSchema(GoGame_schema)
#GoGame_schema['subject'].schemata = 'default'

translCoordDict = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'i':8,'j':9,'k':10,'l':11,'m':12,'n':13,'o':14,'p':15,'q':16,'r':17,'s':18}

class GoGame(ATCTContent):
	"""
	"""

	implements(IGoGame)
	portal_type="Go Game"
	_at_rename_after_creation = True
	schema = GoGame_schema
	
	title = atapi.ATFieldProperty('title')
	description = atapi.ATFieldProperty('description')
	blackPlayer = atapi.ATFieldProperty('blackPlayer')
	blackRating = atapi.ATFieldProperty('blackRating')
	whitePlayer = atapi.ATFieldProperty('whitePlayer')
	whiteRating = atapi.ATFieldProperty('whiteRating')
	komi = atapi.ATFieldProperty('komi')
	handicap = atapi.ATFieldProperty('handicap')
	event = atapi.ATFieldProperty('event')
	place = atapi.ATFieldProperty('place')
	round = atapi.ATFieldProperty('round')
	datePlayed = atapi.ATFieldProperty('datePlayed')
	dateFinished = atapi.ATFieldProperty('dateFinished')
	result = atapi.ATFieldProperty('result')


	def getMove(self,moves,variation,fwd=True):
		"""
		Return an xml for the moves to render
		"""
		root = ET.Element("response")
		for moveNo in moves:
			moveRoot = ET.fromstring(self.variations.getMove(variation,moveNo))
			if fwd:
				for node in moveRoot:
					root.append(node)
			else:
				children = moveRoot.getchildren()
				for i in range(len(children)-1,-1,-1):
					root.append(children[i])
				
		# reverse stone placement when going back
		if not fwd:
			for node in root:
				if node.tag == "addB":
					node.tag = "rmB"
				elif node.tag == "addW":
					node.tag = "rmW"
				elif node.tag == "rmB":
					node.tag = "addB"
				elif node.tag == "rmW":
					node.tag = "addW"
					
		# Add annotations
		if fwd:
			lastMove = max(moves)
		else:
			lastMove = min(moves) - 1
		
		annotDoc = self.variations.getAnnotation(variation,lastMove)
		if annotDoc:
			annotDoc = ET.fromstring(self.variations.getAnnotation(variation,lastMove))
			for node in annotDoc:
				root.append(node)
		
		variations = self.variations.hasVariations(variation,lastMove)
		if variations:
			for varNo in variations:
				ET.SubElement(root,"var",no=str(varNo))
		
		return ET.tostring(root)

	def changeVariation(self,move,currVar,newVar):
		"""
		"""
		root = ET.Element("response")
		moveRoot = ET.fromstring(self.variations.getMove(currVar, move))
		children = moveRoot.getchildren()
		for i in range(len(children)-1,-1,-1):
			root.append(children[i])			
		for node in root:
			if node.tag == "addB":
				node.tag = "rmB"
			elif node.tag == "addW":
				node.tag = "rmW"
			elif node.tag == "rmB":
				node.tag = "addB"
			elif node.tag == "rmW":
				node.tag = "addW"
		moveRoot = ET.fromstring(self.getMove([move],newVar))
		for node in moveRoot:
			root.append(node)

		newVarMoves = self.variations[newVar][0].keys()
		minMove = min(newVarMoves)
		maxMove = max(newVarMoves)
		root.attrib['maxMove'] = str(maxMove)
		root.attrib['minMove'] = str(minMove)
		return ET.tostring(root)

	def parseSgf(self):
		"""
		"""
		
		sgftext = str(self.sgf)
		xmlConv = sgf2xml(sgftext)
		self.event = xmlConv.Event
		self.round = xmlConv.Round
		self.blackPlayer = xmlConv.BlackPlayer
		self.whitePlayer =xmlConv.WhitePlayer
		self.blackRating = xmlConv.BlackRating
		self.whiteRating = xmlConv.WhiteRating
		self.komi = xmlConv.Komi
		self.datePlayed = xmlConv.DatePlayed
		self.dateFinished = xmlConv.DateFinished
		self.place = xmlConv.Place
		self.result = xmlConv.Result
		self.handicap = xmlConv.Handicap
		self.boardSize=xmlConv.BoardSize
		self.variations = xmlConv.variations
		self.noMoves = len(self.variations['0'][0]) - 1

	def setSGF(self,value):
		if not value:
			return
		self.getField('sgf').set(self, value)
		self.parseSgf()
		self.reindexObject()

	
atapi.registerType(GoGame, PROJECTNAME)

def GameModified(object,event):
	"""
	"""
	(tag,rating) = parseRating(object.whiteRating)
	object.setWhiteRating(rating)
	if tag not in object.Subject():
		object.setSubject(object.Subject()+(tag,))
	(tag,rating) = parseRating(object.blackRating)
	object.setBlackRating(rating)
	if tag not in object.Subject():
		object.setSubject(object.Subject()+(tag,))

def parseRating(rating):
	regexp = re.compile('([\d\t]+)([\s]*)([a-zA-Z]+)')
	match = regexp.match(rating)
	rating = ''
	gTag=''
	if match:
		rating = match.group(1)
		if match.group(3) in ['k','kyu','k+','kyu+','k-','kyu-']:
			rating = rating+'kyu'
			gTag = int(match.group(1))
			if gTag in range(1,11):
				gTag = '1-10kyu'
			elif gTag in range(11,21):
				gTag = '11-20kyu'
			else:
				gTag = '20+kyu'
		elif match.group(3) in ['d','dan','d+','dan+','d-','dan-']:
			rating = rating+'dan'
			gTag='dan'
		elif match.group(3) in ['p','pro']:
			rating = rating+'pro'
			gTag = 'pro'
	return (gTag,rating)
