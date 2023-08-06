from Products.CMFCore.utils import getToolByName

def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    originalContext = setup_tool.getImportContextID()
    setup_tool.setImportContext('profile-beyondskins.pyconbrasil2008:default')
    setup_tool.runAllImportSteps()
    setup_tool.setImportContext(originalContext)
    return "Ran all import steps."