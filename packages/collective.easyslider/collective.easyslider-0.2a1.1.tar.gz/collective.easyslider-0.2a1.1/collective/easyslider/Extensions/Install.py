from Products.slideshowfolder.config import *
from Products.CMFCore.utils import getToolByName
from collective.easyslider.interfaces import ISliderPage
from zope.interface import noLongerProvides
try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations

def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.easyslider:default')

def uninstall(portal, reinstall=False):
    
    if not reinstall:
        portal_actions = getToolByName(portal, 'portal_actions')
        object_buttons = portal_actions.object_buttons
    
        actions_to_remove = ('enable_slider', 'disable_slider', 'slider_settings')
        for action in actions_to_remove:
            if action in object_buttons.objectIds():
                object_buttons.manage_delObjects([action])
    
        #remove interfaces
        catalog = portal.portal_catalog
        for item in catalog.searchResults(object_provides=ISliderPage.__identifier__):
            item = item.getObject()
            noLongerProvides(item, ISliderPage)
            item.reindexObject(idxs=['object_provides'])
        
            annotations = IAnnotations(item)
            metadata = annotations.get('collective.easyslider', None)
            if metadata is not None:
                del annotations['collective.easyslider']
    
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.easyslider:uninstall')