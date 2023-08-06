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
    
        #remove interfaces
        catalog = portal.portal_catalog
        items_to_check = catalog.searchResults(object_provides=ISliderPage.__identifier__)
        items_to_check.extend(catalog.searchResults(portal_type=('Folder', 'Collection')))
        for item in items_to_check:
            item = item.getObject()
            noLongerProvides(item, ISliderPage)
            item.reindexObject(idxs=['object_provides'])
        
            annotations = IAnnotations(item)
            metadata = annotations.get('collective.easyslider', None)
            if metadata is not None:
                del annotations['collective.easyslider']
    
    portal_actions = getToolByName(portal, 'portal_actions')
    object_buttons = portal_actions.object_buttons
    object_tabs = portal_actions.object

    actions_to_remove = ('enable_slider', 'disable_slider', 'slider_settings')
    for action in actions_to_remove:
        if action in object_buttons.objectIds():
            object_buttons.manage_delObjects([action])
        if action in object_tabs.objectIds():
            object_tabs.manage_delObjects([action])
    
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.easyslider:uninstall')