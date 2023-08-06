from Products.Five.browser import BrowserView
from zope.interface import Interface, implements
from Products.CMFCore.utils import getToolByName
from plone.app.form import base as ploneformbase
from zope.formlib import form
from collective.easyslider.interfaces import IViewSliderSettings
from plone.app.controlpanel.widgets import AllowedTypesWidget
from collective.easyslider import easyslider_message_factory as _
from zope.app.form.browser import MultiSelectWidget
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from collective.easyslider.settings import ViewSliderSettings
from base import AbstractSliderView
from Acquisition import aq_inner

class SliderViewSettingsForm(ploneformbase.EditForm):
    """
    The page that holds all the slider settings
    """
    form_fields = form.FormFields(IViewSliderSettings)
    #our revised SlidesWidget that only displays slides really
    form_fields['allowed_types'].custom_widget = MultiCheckBoxVocabularyWidget 

    label = _(u'heading_slider_settings_form', default=u"Slider Settings")
    description = _(u'description_slider_settings_form', default=u"Configure the parameters for this slider.")
    form_name = _(u'title_slider_settings_form', default=u"Slider settings")


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
        
        

