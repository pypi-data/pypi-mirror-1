import libxml2
import re
import copy
from qi.Goban.lib.Board import *
from qi.Goban.lib.sgflib import *
from qi.Goban.lib.Variation import *

translCoordDict = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'i':8,'j':9,'k':10,'l':11,'m':12,'n':13,'o':14,'p':15,'q':16,'r':17,'s':18}
translCoordDictInverse = dict( (value, key) for key, value in translCoordDict.iteritems())

class sgf2xml:
    def __init__(self,sgftext):
                    
        self.sgf = sgftext
        self.variations=VariationList()
        self.currentVarNo =0
        self.boardInstances = {}
        parser = SGFParser(self.sgf)
        game = parser.parseOneGame()
        rootNode = game[0]
        self.parseGameInfo(rootNode)
        self.constructMainLine(game)
        self.parseVariations(game,0,{})
        self.variations.chapterizeVariationNames()
    
    def parseGameInfo(self,node):
        """
        """
        if node.has_key('FF'):
            if int(node['FF'].propValue()) != 4:
                raise Exception("Only version 4 of sgf is supported")
        if node.has_key('EV'):
            self.Event = node['EV'].propValue()
        else:
            self.Event=''
        if node.has_key('RO'):
            self.Round=node['RO'].propValue()
        else:
            self.Round=''
        if node.has_key('PB'):
            self.BlackPlayer = node['PB'].propValue()
        else:
            self.BlackPlayer=''
        if node.has_key('PW'):
            self.WhitePlayer=node['PW'].propValue()
        else:
            self.WhitePlayer=''
        if node.has_key('BR'):
            self.BlackRating=node['BR'].propValue()
        else:
            self.BlackRating=''
        if node.has_key('WR'):
            self.WhiteRating=node['WR'].propValue()
        else:
            self.WhiteRating=''
        if node.has_key('KM'):
            self.Komi=node['KM'].propValue()
        else:
            self.Komi=''
        if node.has_key('DT'):
            dates = node['DT'].propValue().split(',')
            self.DatePlayed=dates[0]
            if len(dates) >=2:
                self.DateFinished=dates[1]
            else:
                self.DateFinished=''
        else:
            self.DatePlayed=''
            self.DateFinished=''
        if node.has_key('PC'):
            self.Place=node['PC'].propValue()
        else:
            self.Place=''
        if node.has_key('RE'):
            self.Result=node['RE'].propValue()
        else:
            self.Result=''
        if node.has_key('HA'):
            self.Handicap=node['HA'].propValue()
        else:
            self.Handicap=0
        if node.has_key('SZ'):
            self.BoardSize=int (node['SZ'].propValue())
            if ( self.BoardSize not in [19,13,11,9] ):
                raise Exception("Only 19x19, 13x13, 11x11, and 9x9 gobans are supported."+str(self))
        else:
            self.BoardSize = 19
    
    
    def constructMainLine(self, game):
        """
        """
        annotDiff = {}
        movesDiff = {}
        board = Goban(self.BoardSize)

        # Setup handicap
        node = game[0]
        moveNo = 0
        if node:
            if node.has_key('HA') and int(node['HA'].propValue()) > 0:
                if int(node['HA'].propValue()) > 0:
                    doc = libxml2.newDoc("1.0")
                    root = doc.newChild(None, "response", None)
                    hStones = node['AB'].propValue().split('][')
                    hStones.sort()
                    for stone in hStones:
                        coords = self.translateCoords(stone)
                        board[ (coords[1],coords[0])]=1
                        self.addXMLMove(root, coords)
                    movesDiff[moveNo]=doc.serialize()
                    moveNo = moveNo + 1
            else:
                doc = libxml2.newDoc("1.0")
                root = doc.newChild(None, "response", None)
                movesDiff[moveNo]=doc.serialize()
                moveNo = moveNo + 1
            if node.has_key('C'):
                doc = libxml2.newDoc("1.0")
                root = doc.newChild(None, "response", None)
                nodecomm = node['C'].propValue()
                nodecomm = nodecomm.replace("\]","]")

                comment = root.newChild(None,"comm",None)
                comment.setProp("txt",nodecomm)
                annotDiff[0] = doc.serialize()


        cursor = game.cursor()
        while (True):
            try:
                node = cursor.next()
                moveDoc = self.parseNodeForMoves(node,board)
                movesDiff[moveNo]=moveDoc.serialize()
                if (len(cursor.children)>1):
                    self.boardInstances[(0,moveNo)] = copy.deepcopy(board)

                annotDoc = self.parseNodeForAnnotations(node)
                if annotDoc:
                    annotDiff[moveNo] = annotDoc.serialize()

                moveNo = moveNo +1
            except GameTreeEndError:
                break
        
        self.variations.addVariation(0,(movesDiff,annotDiff,))

    def parseNodeForMoves(self,node,board):
        doc = libxml2.newDoc("1.0")
        root = doc.newChild(None, "response", None)

        if node.has_key('AB'):
            blacks = node['AB'].propValue().split('][')
            blacks.sort()
            for black in blacks:
                coords = self.translateCoords(black)
                if board[(coords[1],coords[0])]==-1:
                    self.addXMLMove(root,coords,False,False)
                self.addXMLMove(root, coords)
                board[(coords[1],coords[0])]=1

        if node.has_key('AW'):
            whites = node['AW'].propValue().split('][')
            whites.sort()
            for white in whites:
                coords = self.translateCoords(white)
                if board[(coords[1],coords[0])]==1:
                    self.addXMLMove(root,coords,False)
                self.addXMLMove(root, coords,True,False)
                board[ (coords[1],coords[0])]=-1
        if node.has_key('AE'):
            toRemove = node['AE'].propValue().split('][')
            for stone in toRemove:
                coords = self.translateCoords(stone)
                if board[(coords[1],coords[0])] == 1:
                    self.addXMLMove(root, coords, False)
                else:
                    if board[(coords[1],coords[0])] == -1:
                        self.addXMLMove(root, coords, False,False)
                board[(coords[1],coords[0])] = 0

        if node.has_key('B'):
            if len(node['B'].propValue()) == 2 and node['B'].propValue()!="tt":
                coords = self.translateCoords(node['B'].propValue())
                self.addXMLMove(root, coords)
                board[ (coords[1],coords[0])]=1
                # Check for captures
                captures = board.checkForCaptures(coords,1)
                for capture in captures:
                    self.addXMLMove(root, capture, False,False)
                    board[(capture[1],capture[0])] = 0
            else:
                passMove = root.newChild(None,"passB",None)

        else:
            if node.has_key('W'):
                if len(node['W'].propValue()) == 2 and node['W'].propValue()!="tt":

                    coords = self.translateCoords(node['W'].propValue())
                    self.addXMLMove(root, coords,True,False)
                    board[ (coords[1],coords[0])]= -1
                    captures = board.checkForCaptures(coords,-1)
                    for capture in captures:
                        self.addXMLMove(root, capture, False,True)
                        board[(capture[1],capture[0])] = 0
                else:
                    passMove = root.newChild(None,"passW",None)
        return doc

    def parseNodeForAnnotations(self,node):
        if node.has_key('C') or node.has_key('LB') or node.has_key('TR') or node.has_key('SQ') or node.has_key('W') or node.has_key('B'):
            doc = libxml2.newDoc("1.0")
            root = doc.newChild(None, "response", None)
            if node.has_key('C'):
                nodecomm = node['C'].propValue()
                nodecomm = nodecomm.replace("\]","]")
                comment = root.newChild(None,"comm",None)
                comment.setProp("txt",nodecomm)
            if node.has_key('LB'):
                annotations = node['LB'].propValue().split('][')
                for ann in annotations:
                    tokens = ann.split(':')
                    coords = self.translateCoords(tokens[0])
                    annotation = root.newChild(None,"annot",None)
                    annotation.setProp("x",str(coords[1]))
                    annotation.setProp("y",str(coords[0]))
                    annotation.setProp("char",tokens[1])
            if node.has_key('TR'):
                triangles = node['TR'].propValue().split('][')
                trianglelist = list()
                for triangle in triangles:
                    if ':' in triangle:
                        range = self.translateRangeCoords(triangle)
                        for item in range:
                            trianglelist.append(item)
                    else:
                        coords = self.translateCoords(triangle)
                        trianglelist.append(coords)
                for triangle in trianglelist:
                    trannot = root.newChild(None,"triangle",None)
                    trannot.setProp("x",str(triangle[1]))
                    trannot.setProp("y",str(triangle[0]))
                    
            if node.has_key('SQ'):
                squares = node['SQ'].propValue().split('][')
                squarelist = list()
                for square in squares:
                    if ':' in square:
                        range = self.translateRangeCoords(square)
                        for item in range:
                            squarelist.append(item)
                    else:
                        coords = self.translateCoords(square)
                        squarelist.append(coords)
                for square in squarelist:
                    trannot = root.newChild(None,"square",None)
                    trannot.setProp("x",str(square[1]))
                    trannot.setProp("y",str(square[0]))
                    
                
            if node.has_key('MA'):
                markups = node['MA'].propValue().split('][')
                markuplist = list()
                for markup in markups:
                    if ':' in markup:
                        range = self.translateRangeCoords(markup)
                        for item in range:
                            markuplist.append(item)
                    else:
                        coords = self.translateCoords(markup)
                        markuplist.append(coords)
                for markup in markuplist:
                    markx = root.newChild(None,"annot",None)
                    markx.setProp("x",str(markup[1]))
                    markx.setProp("y",str(markup[0]))
                    markx.setProp("char",'X')

            if node.has_key('B') or node.has_key('W'):
                if node.has_key('B'):
                    value = node['B'].propValue()
                else:
                    value = node['W'].propValue()
                if len(value) == 2 and value!="tt":
                    coords = self.translateCoords(value)
                    circleannot = root.newChild(None,"circle",None)
                    circleannot.setProp("x",str(coords[1]))
                    circleannot.setProp("y",str(coords[0]))
            return doc
        return None
    
    def parseVariationLine(self,parentVarNo,varNo,line,moveNo):
        annotDiff = {}
        movesDiff = {}
        
        board = copy.deepcopy(self.boardInstances[(parentVarNo,moveNo-1)])
        cursor = line.cursor()
        node = cursor.node
        while (True):
            try:
                moveDoc = self.parseNodeForMoves(node,board)
                movesDiff[moveNo]=moveDoc.serialize()
                annotDoc = self.parseNodeForAnnotations(node)
                if annotDoc:
                    annotDiff[moveNo] = annotDoc.serialize()
                if (len(cursor.children)>1):
                    self.boardInstances[(varNo,moveNo)] = copy.deepcopy(board)
                node = cursor.next()
                moveNo = moveNo +1
            except GameTreeEndError:
                break
        return (movesDiff,annotDiff,)
    
    def parseVariations(self,gametree,parentVarNo,foundBranchMoves):
        """
        """
        
        if gametree.variations:
            if len(gametree.variations)>1:
                for i in range(1,len(gametree.variations)):
                    cursor = gametree.cursor()
                    cursor.reset()
                    foundBranch = 0
                    while not foundBranch:
                        if len(cursor.children)>1:
                            foundBranch = foundBranch +1
                        try:
                            node = cursor.next()
                        except GameTreeEndError:
                            break
                    branchAtMove = cursor.nodenum

                    if foundBranchMoves.has_key(parentVarNo):
                        branchAtMove = branchAtMove + foundBranchMoves[parentVarNo]
                    if i==(len(gametree.variations)-1):
                        foundBranchMoves[parentVarNo]= branchAtMove
                    
                        
                    self.currentVarNo = self.currentVarNo +1
                    foundBranchMoves[self.currentVarNo] = branchAtMove
                    varMainline = gametree.variations[i]

                    self.variations.addVariation(self.currentVarNo,self.parseVariationLine(parentVarNo,self.currentVarNo,varMainline,branchAtMove),branchAtMove,parentVarNo)
                    
                    self.parseVariations(gametree.variations[i],self.currentVarNo,foundBranchMoves)
            self.parseVariations(gametree.variations[0],parentVarNo,foundBranchMoves)
  
    
    def addXMLMove(self, root,coords,add=True,black=True):
        if add:
            if black:
                move = root.newChild(None, "addB", None)
            else:
                move = root.newChild(None, "addW", None)
        else:
            if black:
                move = root.newChild(None, "rmB", None)
            else:
                move = root.newChild(None, "rmW", None)
        move.setProp("x", str(coords[1]))
        move.setProp("y", str(coords[0]))
        return
    def translateCoords(self,sCoord):
        return (translCoordDict[sCoord[0]],translCoordDict[sCoord[1]])

    def translateCoordsInverse(self,sCoord):
        return (translCoordDictInverse [sCoord[0]],translCoordDictInverse[sCoord[1]])

    def translateRangeCoords(self,rCoord):
        rCoord = rCoord.split(':')
        first = self.translateCoords(rCoord[0])
        last = self.translateCoords(rCoord[1])
        coordList = list()
        if first[0] == last[0]:
            coordList = [ (first[0],j) for j in range(first[1],last[1]+1) ]
        else:
            coordList = [ (i,first[1]) for i in range(first[0],last[0]+1) ]
        return coordList
