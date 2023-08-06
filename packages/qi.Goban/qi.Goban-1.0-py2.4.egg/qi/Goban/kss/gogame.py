from kss.core import KSSView
from datetime import datetime
from elementtree.ElementTree import XML as parseET

class GoGameKSS(KSSView):
	"""
	"""
	def __init__(self, *args):
		KSSView.__init__(self, *args)
		self.game = self.context.aq_inner
		self.core = self.getCommandSet('core')
		self.gobankss = self.getCommandSet('goban')

	def gameInit(self):
		"""
		"""
		self.core.setStateVar("gogame-moveNo","-1")		   
		self.core.setStateVar("gogame-maxMove",str(self.game.noMoves))
		self.core.setStateVar("gogame-minMove","0")
		self.core.setStateVar("gogame-variation","0")
		stones = "{'b':[],'w':[],'bt':[],'wt':[],'bs':[],'ws':[]}"
		self.core.setStateVar("gogame-stones",stones)
		self._drawHoshi()
		self._jumpToMove(0,-1,"0",0,self.game.noMoves,stones)
		return self.render()		

	def fwdMove(self,moveNo,variation,minMove,maxMove,stones):
		moveNo = int(moveNo)
		minMove = int(minMove)
		maxMove = int(maxMove)
		self._jumpToMove(moveNo+1,moveNo,variation,minMove,maxMove,stones)
		return self.render()	

	def backMove(self,moveNo,variation,minMove,maxMove,stones):
		moveNo = int(moveNo)
		minMove = int(minMove)
		maxMove = int(maxMove)
		self._jumpToMove(moveNo-1,moveNo,variation,minMove,maxMove,stones)
		return self.render()	
	
	def ffwdMove(self,moveNo,variation,minMove,maxMove,stones):
		moveNo = int(moveNo)
		minMove = int(minMove)
		maxMove = int(maxMove)
		self._jumpToMove(moveNo+10,moveNo,variation,minMove,maxMove,stones)
		return self.render()	
	
	def rwndMove(self,moveNo,variation,minMove,maxMove,stones):
		moveNo = int(moveNo)
		minMove = int(minMove)
		maxMove = int(maxMove)
		self._jumpToMove(moveNo-10,moveNo,variation,minMove,maxMove,stones)
		return self.render()	

	def varChange(self,moveNo,variation,newVar,stones):
		moveNo = int(moveNo)
		xml = self.game.changeVariation(int(moveNo),variation,newVar)
		self.core.setStateVar("gogame-variation",newVar)
		self.renderMoves(xml, moveNo, newVar,stones)
		return self.render()

	def _jumpToMove(self,newMove,moveNo,variation,minMove,maxMove,stones):
		"""
		"""
		if newMove > maxMove:
			newMove = maxMove
		elif newMove < minMove:
			newMove = minMove
		if newMove == moveNo:
			return
		
		if newMove>moveNo:
			fwd = True
			moves = range(moveNo+1,newMove+1)
		else:
			fwd = False
			moves = range(moveNo,newMove,-1)
		self.core.setStateVar("gogame-moveNo",str(newMove))
		xml = self.game.getMove(moves,variation,fwd) 
		self.renderMoves(xml,newMove,variation,stones)
	
	def renderMoves(self,xml,moveNo,variation,stones):
		stones=eval(stones)
		xmlDoc = parseET(xml)
		if "minMove" in xmlDoc.keys():
			self.core.setStateVar("gogame-minMove",xmlDoc.attrib["minMove"])
		if "maxMove" in xmlDoc.keys():		  
			self.core.setStateVar("gogame-maxMove",xmlDoc.attrib["maxMove"])

					
		#Add variations
		variations = xmlDoc.findall("var")
		varOptions = '<option selected="selected">'+variation+'</option>'
		for altVar in variations:
			varOptions = varOptions + "<option>"+altVar.attrib["no"]+"</option>"
		if variations:
			varSelect = '<select id="varSelect" class="hasVarSelect">'+varOptions+'</select>'		
		else:
			varSelect = '<select id="varSelect">'+varOptions+'</select>'
		self.core.replaceHTML('#varSelect',varSelect)
		
		#Clear annotations
		
		previousAnnotations = self.core.getCssSelector(".goLabel1C")		
		self.core.deleteNode(previousAnnotations)
		previousAnnotations = self.core.getCssSelector(".goLabel2C")		
		self.core.deleteNode(previousAnnotations)
		
		#Set new annotations
		annotations = xmlDoc.findall("annot")
		for node in annotations:
			x = node.attrib["x"]
			y = node.attrib["y"]
			c = node.attrib["char"]
			td = self.core.getHtmlIdSelector(x+"-"+y)
			if len(c)==1:
				label = '<span class="goLabel1C">'+c+'</span>'
			else:
				label = '<span class="goLabel2C">'+c+'</span>'
			self.core.insertHTMLAfter(td,label)
		
		#Set last move circle
		node = xmlDoc.findall("circle")
		if node:
			x = node[0].attrib["x"]
			y = node[0].attrib["y"]
			td = self.core.getHtmlIdSelector(x+"-"+y)
			label = '<span class="goLabel1C">o</span>'
			self.core.insertHTMLAfter(td,label)
		
		#Triangles
		for tdid in stones['bt']:
			td = self.core.getHtmlIdSelector(tdid)
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/b.png")
		stones['bt']=[]
		for tdid in stones['wt']:
			td = self.core.getHtmlIdSelector(tdid)
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/w.png")
		stones['wt']=[]
		nodes = xmlDoc.findall("triangle")
		for node in nodes:
			x = node.attrib["x"]
			y = node.attrib["y"]
			tdid = x+"-"+y
			td = self.core.getHtmlIdSelector(tdid)
			if tdid in stones['b']:
				self.core.setAttribute(td,"src","++resource++qi.Goban.images/bt.png")
				stones['bt'].append(tdid)
			elif tdid in stones['w']:
				self.core.setAttribute(td,"src","++resource++qi.Goban.images/wt.png")
				stones['wt'].append(tdid)

		#Squares
		for tdid in stones['bs']:
			td = self.core.getHtmlIdSelector(tdid)
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/b.png")
		stones['bs']=[]
		for tdid in stones['ws']:
			td = self.core.getHtmlIdSelector(tdid)
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/w.png")
		stones['ws']=[]
		nodes = xmlDoc.findall("square")
		for node in nodes:
			x = node.attrib["x"]
			y = node.attrib["y"]
			tdid = x+"-"+y
			td = self.core.getHtmlIdSelector(tdid)
			if tdid in stones['b']:
				self.core.setAttribute(td,"src","++resource++qi.Goban.images/bs.gif")
				stones['bs'].append(tdid)
			elif tdid in stones['w']:
				self.core.setAttribute(td,"src","++resource++qi.Goban.images/ws.gif")
				stones['ws'].append(tdid)

		# Draw stones		
		for node in xmlDoc:
			if node.tag in ['addB','addW']:
				self._drawStone(node,stones)
			elif node.tag in ['rmB','rmW']:
				self._removeStone(node,stones)

		
		#Set comment
		commTxt = self.core.getHtmlIdSelector("commTxt")
		node = xmlDoc.findall("comm")
		if node:
			txt = node[0].attrib["txt"]
			self.core.replaceInnerHTML(commTxt,txt)
		else:
			self.core.replaceInnerHTML(commTxt,"")

		#Set move counter
		self.gobankss.setInputValue('#moveCounter',str(moveNo))

		self.core.setStateVar('gogame-stones',str(stones))
		
	def _drawStone(self,node,stones):
		"""
		"""
		x = node.attrib['x']
		y = node.attrib['y']
		td = self.core.getHtmlIdSelector(x+'-'+y)

		if node.tag=="addB":
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/b.png")
			stones['b'].append(x+'-'+y)
		else:
			self.core.setAttribute(td,"src","++resource++qi.Goban.images/w.png")			
			stones['w'].append(x+'-'+y)

	def _removeStone(self,node,stones):
		"""
		"""
		
		x = int(node.attrib['x'])
		y = int(node.attrib['y'])
		tdid = str(x)+'-'+str(y)
		if node.tag=="rmB":	
			stones['b'].remove(tdid)
		elif node.tag=="rmW":
			stones['w'].remove(tdid)
		
		if tdid in stones['b'] or tdid in stones['w']:
			return
			
		td = self.core.getHtmlIdSelector(tdid)
		
		bSize = self.game.boardSize
		# No borders
		if x>0 and x<(bSize-1) and y>0 and y<(bSize-1): 
			if tdid in ['3-3','3-9','3-15','9-3','9-9','9-15','15-3','15-9','15-15']:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/hp.gif")
			else:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/ep.gif")
		# Top border
		elif x==0:
			if y==0:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/tl.gif")
			elif y==(bSize-1):
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/tr.gif")
			else:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/tp.gif")
		elif x==bSize-1:
			if y==0:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/bl.gif")
			elif y==(bSize-1):
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/br.gif")
			else:
				self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/bp.gif")
		elif y==0:
			self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/lp.gif")
		else:
			self.core.setAttribute(td, name="src",value="++resource++qi.Goban.images/rp.gif")
		
		
	def _drawHoshi(self):
		"""
		Draw hoshi points for 19x19 boards
		"""
		
		if self.game.boardSize == 19:
			for i in range(3,16,6):
				for j in range(3,16,6):
					node = self.core.getHtmlIdSelector(str(i)+'-'+str(j))
					self.core.setAttribute(node, name="src",value="++resource++qi.Goban.images/hp.gif")
			
