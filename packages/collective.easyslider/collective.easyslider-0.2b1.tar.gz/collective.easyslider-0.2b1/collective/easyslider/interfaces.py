from zope.interface import Interface, Attribute
from zope import schema
from collective.easyslider import easyslider_message_factory as _

class ISliderLayer(Interface):
    """
    marker interface for slider layer
    """

class ISliderPage(Interface):
    """
    marker interface for a page that implements
    the Slider 
    """

class ISliderUtilProtected(Interface):
    
    def enable():
        """
        enable slider on this object
        """
    
    def disable():
        """
        disable slider on this object
        """
        
class ISliderUtil(Interface):
    
    def enabled():
        """
        checks if slider is enabled on the peice of content
        """
    
class ISliderSettings(Interface):
    """
    The actual slider settings
    """
    
    width = schema.Int(
        title=_(u'label_width_title_slider_setting', default=u"Width"),
        description=_(u"label_width_description_slider_setting", 
            default=u"The fixed width of the slider."),
        default=600,
        required=True
    )
    
    height = schema.Int(
        title=_(u'label_height_title_slider_setting', default=u"Height"),
        description=_(u"label_height_description_slider_setting", 
            default=u"The fixed height of the slider."),
        default=230,
        required=True
    )
    
    show = schema.Bool(
        title=_(u"label_show_title_slider_setting", default=u"Show it?"),
        description=_(u"label_show_description_slider_setting",
            default=u"Do you want the easy slider to show on this page?"),
        default=True,
        required=True
    )

    vertical = schema.Bool(
        title=_(u"label_vertical_title_slider_setting", default=u"Vertical?"),
        description=_(u"label_vertical_description_slider_setting", 
            default=u"Should the slide transition vertically?"),
        default=False
    )
    
    speed = schema.Int(
        title=_(u"label_speed_title_slider_setting", default=u"Speed"),
        description=_(u"label_speed_description_slider_setting",
            default=u"Speed at which the slide will transition."),
        default=800
    )
    
    slides = schema.List(
        title=_(u"label_slides_title_slider_setting", default=u"Slides"),
        description=_(u"label_slides_description_slider_settings",
            default=u"These are the slides that will show up in the easySlider for this page."),
        default=[]
    )
    
    
class ISlide(Interface):
    
    slide = schema.Text(
        title=_(u"label_slide_title_slider_setting", default=u"Slide")
    )
    
class ISlidesContext(Interface):
    """
    Context to allow traversing to the slides list
    """
    
class ISlideContext(Interface):
    """
    Context to allow traversing to a slide on a ISlidesContext object
    """
    index = Attribute("""Index of the slide on the object""")