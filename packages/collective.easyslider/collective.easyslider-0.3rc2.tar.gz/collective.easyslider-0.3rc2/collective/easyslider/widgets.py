from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from utils import slider_settings_css

class SlidesWidget(SimpleInputWidget):
    """
    this widget pretty much is the same as the Slides view
    In itself, it does not provide any data manipulatation, but
    it does provide the correct urls to perform the editing action
    for each slide
    """
    
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
