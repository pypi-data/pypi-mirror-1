from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
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
    top:-%(next_top)ipx
}
#prevBtn{
	top:-%(prev_top)ipx;
}	
""" % {
            'width' : self.settings.width,
            'height' : self.settings.height,
            'next_top' : ((self.settings.height/2) + 75) + 50,
            'prev_top' : ((self.settings.height/2) + 50)
        }
        
    def js(self):
        return """
jQuery(document).ready(function(){	
	jQuery("#slider").easySlider({
	    speed : %(speed)i,
	    orientation: '%(orientation)s'
	});
});
        """ % {
            'speed' : self.settings.speed,
            'orientation' : self.settings.vertical and 'vertical' or ''
        }
        

    def update(self):
        super(EasySlider, self).update()
        
        if not ISliderPage.providedBy(self.context):
            self.show = False
        else:
            self.settings = SliderSettings(self.context)
            self.show = self.settings.show