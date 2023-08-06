from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from redomino.autodelete.config import PROJECTNAME

def setupVarious(context):
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('redomino.autodelete_various.txt') is None:
        return
        
    # additional setup code
    setup_maintenance(context)

def setup_maintenance(context):
    """ Adds the redomino.autodelete setup scripts, if PloneMaintenance is available """
    portal = context.getSite()
    portal_maintenance = getToolByName(portal, 'portal_maintenance', None)

    if portal_maintenance:
        scriptsholder = getattr(portal_maintenance, 'scripts', None)
    
        # redomino.autodelete maintenance script
        if not scriptsholder.hasObject('runAutodelete'):
            manage_addExternalMethod(scriptsholder,
                                     'runAutodelete',
                                     'Delete the expired content',
                                     PROJECTNAME+'.maintenance_utils',
                                     'runAutodelete')
        else:
            # reload of existing external method
            ext_method = getattr(scriptsholder, 'runAutodelete')
            ext_method.reloadIfChanged()
        
