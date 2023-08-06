from zope import interface
from zope import component
from p4a.image import interfaces

import p4a.z2utils #Patch CMFDynamicViewFTI
p4a.z2utils # pyflakes

from Products.CMFDynamicViewFTI import interfaces as cmfdynifaces

class ImageContainerDynamicViews(object):
    
    interface.implements(cmfdynifaces.IDynamicallyViewable)
    component.adapts(interfaces.IImageContainerEnhanced)

    def __init__(self, context):
        self.context = context # Actually ignored...
        
    def getAvailableViewMethods(self):
        """Get a list of registered view method names
        """
        return [view for view, name in self.getAvailableLayouts()]

    def getDefaultViewMethod(self):
        """Get the default view method name
        """
        return "image-container.html"

    def getAvailableLayouts(self):
        """Get the layouts registered for this object.
        """        
        return (("image-container.html", "Image view"),)
