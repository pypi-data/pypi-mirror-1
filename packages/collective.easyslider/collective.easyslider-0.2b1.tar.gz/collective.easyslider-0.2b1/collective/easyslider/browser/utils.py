from zope.interface import implements, alsoProvides, noLongerProvides
from Products.Five.browser import BrowserView
from collective.easyslider.interfaces import *

try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations


class SliderUtilProtected(BrowserView):
    """
    a protected traverable utility for 
    enabling and disabling sliders
    """
    implements(ISliderUtilProtected)
    def enable(self):
        if not ISliderPage.providedBy(self.context):
            alsoProvides(self.context, ISliderPage)
            self.context.reindexObject(idxs=['object_provides'])
            
            #now delete the annotation
            annotations = IAnnotations(self.context)
            metadata = annotations.get('collective.easyslider', None)
            if metadata is not None:
                del annotations['collective.easyslider']
            
            
        self.request.response.redirect(self.context.absolute_url() + "/@@slider-settings")
        
    def disable(self):
        if ISliderPage.providedBy(self.context):
            noLongerProvides(self.context, ISliderPage)
            self.context.reindexObject(idxs=['object_provides'])
            
        self.request.response.redirect(self.context.absolute_url())
        
        
class SliderUtil(BrowserView):
    """
    a public traverable utility that checks if a 
    slide is enabled
    """
    implements(ISliderUtil)
    def enabled(self):
        return ISliderPage.providedBy(self.context)    
