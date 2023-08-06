from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.Five.browser import BrowserView
from zope.formlib import form
from plone.app.form import base as ploneformbase
from collective.easyslider.interfaces import *
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from collective.easyslider import easyslider_message_factory as _
from zope.interface import implements
from zope.component import adapts
from collective.easyslider.widgets import SlidesWidget
from collective.easyslider.settings import SliderSettings
from collective.easyslider.utils import slider_settings_css

class SliderPageSettingsForm(ploneformbase.EditForm):
    """
    The page that holds all the slider settings
    """
    form_fields = form.FormFields(ISliderSettings)
    #our revised SlidesWidget that only displays slides really
    form_fields['slides'].custom_widget = SlidesWidget 

    label = _(u'heading_slider_settings_form', default=u"Slider Settings")
    description = _(u'description_slider_settings_form', default=u"Configure the parameters for this slider.")
    form_name = _(u'title_slider_settings_form', default=u"Slider settings")
    
    
class AddSlideAdapter(SchemaAdapterBase):
    """
    Since AddSlideForm is for an ISlideContext,
    we create this adapter so it is called to
    populate the slides
    """
    adapts(ISlideContext)
    implements(ISlide)
    
    def __init__(self, context):
        super(AddSlideAdapter, self).__init__(context)
        
        self.settings = SliderSettings(context.context)
        
        if context.index > (len(self.settings.slides) -1) or context.index < 0:
            #a valid index was not specified, just create a new one...
            context.index = -1
    
    def get_slide(self):
        if self.context.index == -1: # creating new
            return ""
        else:
            return self.settings.slides[self.context.index]
        
    def set_slide(self, value):
        slides = self.settings.slides
        
        if self.context.index == -1:
            slides.append(value)
            self.context.index = len(slides) - 1
        else:
            slides[self.context.index] = value
            
        self.settings.slides = slides
        
    slide = property(get_slide, set_slide)
    
    
class AddSlideForm(ploneformbase.EditForm):
    """
    The add/edit form for a slide
    """
    form_fields = form.FormFields(ISlide)
    form_fields['slide'].custom_widget = WYSIWYGWidget
    
    template = ViewPageTemplateFile('updateslide.pt')
    
    label = _(u'heading_add_slide_form', default=u"")
    description = _(u'description_add_slide_form', default=u"")
    form_name = _(u'title_add_slide_form', default=u"Add/Update Slide")
    
    def __init__(self, context, request):
        super(AddSlideForm, self).__init__(context, request)
            
        
class SlidesView(BrowserView):
    """
    View of all the slides
    This uses the same page template as the slides widget--just a different __init__ method
    to setup the call_context and css members
    """
    template = ViewPageTemplateFile('slides.pt')
    
    def __init__(self, context, request):
        super(SlidesView, self).__init__(context, request)
        
        self.settings = SliderSettings(context.context)
        self.call_context = self.context.context
        self.css = slider_settings_css(self.settings) # since this uses the same .pt file
        
    def __call__(self):
        return self.template()
        
        
class SlideView(BrowserView):
    """
    For doing operations on a slide
    """
    
    def __init__(self, context, request):
        super(SlideView, self).__init__(context, request)
        self.settings = SliderSettings(context.context)
    
    def move_up(self, ajax=None):
        
        if self.context.index > 0:
            slides = self.settings.slides
            index = self.context.index
        
            tmp = slides[index-1]
            slides[index-1] = slides[index]
            slides[index] = tmp
        
            self.settings.slides = slides
        
        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'
        
    def move_down(self, ajax=None):
        
        if self.context.index < len(self.settings.slides):
            slides = self.settings.slides
            index = self.context.index
        
            tmp = slides[index+1]
            slides[index+1] = slides[index]
            slides[index] = tmp
        
            self.settings.slides = slides
        
        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'
            
    def remove(self, ajax=None):
        if self.context.index < len(self.settings.slides) and self.context.index >= 0:
            slides = self.settings.slides
            del slides[self.context.index]
            self.settings.slides = slides

        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'
