from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from OFS.SimpleItem import SimpleItem
from zope.publisher.interfaces.browser import IBrowserPublisher
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.Five.browser import BrowserView
from zope.formlib import form
from plone.app.form import base as ploneformbase
from collective.easyslider.interfaces import *
from zope.interface import alsoProvides, noLongerProvides
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from collective.easyslider import easyslider_message_factory as _
from zope.interface import Interface, implements
from zope.component import adapts
from collective.easyslider.widgets import SlidesWidget
from collective.easyslider.settings import SliderSettings
from collective.easyslider.utils import slider_settings_css
try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations


class SliderPageSettingsForm(ploneformbase.EditForm):
    """
    """
    form_fields = form.FormFields(ISliderSettings)
    form_fields['slides'].custom_widget = SlidesWidget

    label = _(u'heading_slider_settings_form', default=u"slider settings")
    description = _(u'description_slider_settings_form', default=u"Configure the parameters for this slider.")
    form_name = _(u'title_slider_settings_form', default=u"Slider settings")
    
class SlideContext(SimpleItem):
    """ 
    This is a transient item that allows us to traverse through (a wrapper of) a slide
    from a wrapper of a slides list on an object
    """
    implements(ISlideContext, IBrowserPublisher)
    
    def __init__(self, context, request, index=-1):
        super(SlideContext, self).__init__(context, request)
        self.context = context
        self.request = request
        self.index = index
    
    def publishTraverse(self, traverse, name):
        """ shouldn't go beyond this
        """
        return self
    
    def browserDefault(self, request):
        """ Can't really traverse to anything else
        """
        return self, ('@@edit',)
        
    def absolute_url(self):
        return self.context.absolute_url() + "/slides/" + str(self.index)
    
class SlidesContext(SimpleItem):
    """ 
    This is a transient item that allows us to traverse through (a wrapper of) a slides
    list on an object
    """
    # Implementing IBrowserPublisher tells the Zope 2 publish traverser to pay attention
    # to the publishTraverse and browserDefault methods.
    implements(ISlidesContext, IBrowserPublisher)
    
    def __init__(self, context, request):
        super(SlidesContext, self).__init__(context, request)
        self.context = context
        self.request = request
    
    def publishTraverse(self, traverse, index):
        """ Look up the index whose name matches the next URL path element, and wrap it.
        """
        return SlideContext(self.context, self.request, int(index)).__of__(self)
    
    def browserDefault(self, request):
        """ if nothing specified, create new slide
        """
        return self, ('@@view',)
        
    def absolute_url(self):
        return self.context.absolute_url() + "/slides"
    
class AddSlideAdapter(SchemaAdapterBase):
    
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
    form_fields = form.FormFields(ISlide)
    form_fields['slide'].custom_widget = WYSIWYGWidget
    
    template = ViewPageTemplateFile('updateslide.pt')
    
    label = _(u'heading_add_slide_form', default=u"")
    description = _(u'description_add_slide_form', default=u"")
    form_name = _(u'title_add_slide_form', default=u"Add/Update Slide")
    
    def __init__(self, context, request):
        super(AddSlideForm, self).__init__(context, request)
    
class SliderUtilProtected(BrowserView):
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
    implements(ISliderUtil)
    def enabled(self):
        return ISliderPage.providedBy(self.context)    
        
class SlidesView(BrowserView):
    
    template = ViewPageTemplateFile('slides.pt')
    
    def __init__(self, context, request):
        super(SlidesView, self).__init__(context, request)
        
        self.settings = SliderSettings(context.context)
        self.call_context = self.context.context
        self.css = slider_settings_css(self.settings) # since this uses the same .pt file
        
    def __call__(self):
        return self.template()
        
class SlideView(BrowserView):
    
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
