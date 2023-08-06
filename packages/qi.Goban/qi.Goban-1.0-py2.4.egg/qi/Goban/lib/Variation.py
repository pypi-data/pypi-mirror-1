import copy

class VariationList(dict):
    def __init__(self):
        dict.__init__(self)
        self.variationTree = dict()
        
    
    def addVariation(self,varId,movesAndAnnotations,branchMove=0,parentId=None):
        self[varId] = movesAndAnnotations
        self.variationTree[varId]=dict()
        if not parentId is None:
            pDict = self.variationTree[parentId]
            if not pDict.has_key(branchMove):
                pDict[branchMove] = list()
            pDict[branchMove].append(varId)
            self.variationTree[parentId] = pDict
            self.variationTree[varId][branchMove]=[parentId]
    
    
    def chapterizeVariationNames(self):
        newVarNames = dict()
        newVarNames[0]='0'
        self.chapterizeVariation(0,newVarNames)
        for key in self.keys():
            self[newVarNames[key]] = self[key]
            del self[key]
        for key in self.variationTree.keys():
            newMoveDict = dict()
            for move in self.variationTree[key]:
                newMoveDict[move] = [newVarNames[childVar] for childVar in self.variationTree[key][move] ]
            self.variationTree[newVarNames[key]] = newMoveDict
            del self.variationTree[key]
        
    def chapterizeVariation(self,key,newVarNames):
        parentName = newVarNames[key]        
        childVariations = list()
        for move in self.variationTree[key].keys():
            childVarsAtMove = self.variationTree[key][move]
            for child in childVarsAtMove:
                    childVariations.append(child)
        childVariations = [item for item in childVariations if item > key]
        childVariations.sort()
        for i in range(0,len(childVariations)):
            newVarNames[childVariations[i]]=parentName+'.'+str(i+1)
            self.chapterizeVariation(childVariations[i],newVarNames)
          
    def hasVariations(self,varid,moveNo):
        if self.variationTree[varid].has_key(moveNo):
            return self.variationTree[varid][moveNo]
        return None
    
    def getMove(self,varid,moveNo):
        return self[varid][0][moveNo]
        
    def getAnnotation(self,varid,moveNo):
        if self[varid][1].has_key(moveNo):        
            return self[varid][1][moveNo]
    
        
                
    
        
        
    