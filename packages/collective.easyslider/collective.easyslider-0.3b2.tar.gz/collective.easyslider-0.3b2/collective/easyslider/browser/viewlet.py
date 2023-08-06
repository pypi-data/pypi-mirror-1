from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from collective.easyslider.settings import PageSliderSettings
from collective.easyslider.interfaces import ISliderPage
from base import AbstractSliderView

class EasySlider(ViewletBase, AbstractSliderView):

    render = ViewPageTemplateFile('viewlet.pt')

    def update(self):
        super(EasySlider, self).update()
        self.settings = PageSliderSettings(self.context)
        
        if not ISliderPage.providedBy(self.context) or len(self.settings.slides) == 0:
            self.show = False
        else:
            self.show = self.settings.show