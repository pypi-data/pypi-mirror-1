from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from collective.easyslider.settings import PageSliderSettings
from collective.easyslider.interfaces import ISliderPage
from base import AbstractSliderView

class EasySlider(ViewletBase, AbstractSliderView):

    render = ViewPageTemplateFile('viewlet.pt')

    def update(self):
        super(EasySlider, self).update()
        
        if not ISliderPage.providedBy(self.context):
            self.show = False
        else:
            self.settings = PageSliderSettings(self.context)
            self.show = self.settings.show