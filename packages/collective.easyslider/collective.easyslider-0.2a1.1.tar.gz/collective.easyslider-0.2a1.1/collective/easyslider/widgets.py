from zope.schema.interfaces import ValidationError
from zope.component import getMultiAdapter

from zope.app.form.interfaces import WidgetInputError
from zope.app.form.browser.interfaces import \
    ISourceQueryView, ITerms, IWidgetInputErrorView
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.vocabularies.interfaces import IBrowsableTerm
from utils import slider_settings_css

class SlidesWidget(SimpleInputWidget):
    
    template = ViewPageTemplateFile('browser/slides.pt')

    def __init__(self, field, request):
        
        SimpleInputWidget.__init__(self, field, request)
        
        self.call_context = self.context.context.context # field/settings/context
        self.settings = self.context.context
        self.css = slider_settings_css(self.settings) # since this uses the same .pt file

    def __call__(self):
        return self.template(self)

    def hasInput(self):
        """
        data should never change here....
        """
        return False
