from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from collective.easyslider.settings import SliderSettings
from collective.easyslider.interfaces import ISliderPage

class EasySlider(ViewletBase):

    render = ViewPageTemplateFile('viewlet.pt')

    def css(self):
        return """
#slider-container{
    margin: auto;
    width: %(width)ipx;
    height: %(height)ipx;
}
#slider, #slider li{ 
    width:%(width)ipx;
    height:%(height)ipx;
}
#nextBtn{ 
    left:%(width)ipx;
}""" % {
            'width' : self.settings.width,
            'height' : self.settings.height
        }
        
    def js(self):
        return """
jQuery(document).ready(function(){	
	jQuery("#slider").easySlider();
});
        """
        

    def update(self):
        super(EasySlider, self).update()
        
        if not ISliderPage.providedBy(self.context):
            self.show = False
        else:
            self.settings = SliderSettings(self.context)
            self.show = self.settings.show