

class AbstractSliderView(object):
    """
    must have settings attribute specified
    """
    
    def css(self):
        return """
#slider-container{
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
	    vertical: %(vertical)s,
	    auto : %(auto)s,
	    pause : %(pause)i,
	    continuous : %(continuous)s,
	    goToButtons: %(show_go_to)s
	});
});
        """ % {
            'speed' : self.settings.speed,
            'vertical' : str(self.settings.vertical).lower(),
            'auto' : str(self.settings.auto).lower(),
            'pause' : self.settings.pause,
            'continuous' : str(self.settings.continuous).lower(),
            'show_go_to' : str(self.settings.show_go_to).lower()
        }