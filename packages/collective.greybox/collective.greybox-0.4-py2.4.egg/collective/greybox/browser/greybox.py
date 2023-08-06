from Products.Five.browser import BrowserView
from collective.greybox.interfaces import IGreyBoxView
from zope.interface import implements

class greyBox(BrowserView):
    """
    perhaps we can readout some properties from a configlet....perhabs.
    """
    
    implements(IGreyBoxView)
    
    def getImages(self):
        context = self.context
        images = [obj for obj in context.getFolderContents(full_objects=True) if obj.Type() == 'Image']
        return images
    
    def getOtherObjs(self):
        context = self.context
        others = [obj for obj in context.getFolderContents() if obj.portal_type != 'Image']
        return others    
