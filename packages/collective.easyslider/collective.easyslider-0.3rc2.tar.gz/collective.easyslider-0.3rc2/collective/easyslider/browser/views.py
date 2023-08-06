from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.form import base as ploneformbase
from zope.formlib import form
from collective.easyslider.interfaces import IViewSliderSettings
from collective.easyslider import easyslider_message_factory as _
from collective.easyslider.settings import PageSliderSettings, ViewSliderSettings
from base import AbstractSliderView
from Acquisition import aq_inner
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.easyslider.utils import slider_settings_css

class SliderView(BrowserView, AbstractSliderView):
    
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)        
        self.settings = ViewSliderSettings(context)
    
    def get_items(self):
        if self.context.portal_type == "Folder":
            catalog = getToolByName(self.context, 'portal_catalog')
            res = catalog.searchResults(
                path='/'.join(self.context.getPhysicalPath()),
                portal_type=self.settings.allowed_types,
                limit=self.settings.limit
            )
        else:
            res = aq_inner(self.context).queryCatalog(
                portal_type=self.settings.allowed_types,
                limit=self.settings.limit
            )
            
        if self.settings.limit == 0:
            return res
        else:
            return res[:self.settings.limit]
        
        

class SlidesView(BrowserView):
    """
    View of all the slides
    This uses the same page template as the slides widget--just a different __init__ method
    to setup the call_context and css members
    """
    template = ViewPageTemplateFile('slides.pt')

    def __init__(self, context, request):
        super(SlidesView, self).__init__(context, request)

        self.settings = PageSliderSettings(context.context)
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
        self.settings = PageSliderSettings(context.context)

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
