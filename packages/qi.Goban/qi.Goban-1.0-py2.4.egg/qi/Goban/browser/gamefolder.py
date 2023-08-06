from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class GameFolderView(BrowserView):
    """
    """
    __call__ = ViewPageTemplateFile('gamefolder.pt')
    
    def batchListing(self):
        """
        """
        return self.context.getFolderContents({'portal_type':'Go Game'},
                                              batch=True,b_size=20,full_objects=True)
