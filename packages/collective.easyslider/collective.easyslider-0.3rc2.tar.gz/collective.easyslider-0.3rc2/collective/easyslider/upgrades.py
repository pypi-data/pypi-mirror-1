
default_profile = 'profile-collective.easyslider:default'

def upgrade_from_0_3rc1__to__0_3rc2(context):
    context.runImportStepFromProfile(default_profile, 'viewlets')
    context.runImportStepFromProfile(default_profile, 'portlets')
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    context.runImportStepFromProfile(default_profile, 'cssregistry')
    
def upgrade_to_0_3rc2(context):
    #just run all since you don't know what version was previously used
    
    context.runAllImportStepsFromProfile(default_profile)
    