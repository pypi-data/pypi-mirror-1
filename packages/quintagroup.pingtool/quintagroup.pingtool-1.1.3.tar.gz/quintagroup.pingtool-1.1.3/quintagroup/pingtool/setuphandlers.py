from Products.CMFCore.utils import getToolByName
from quintagroup.pingtool.config import SITES_LIST, PROJECTNAME

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('%s_various.txt' % PROJECTNAME) is None:
        return

    # Add additional setup code here
    portal = context.getSite()
    existent_sites = portal.portal_pingtool.objectIds()
    for site in SITES_LIST:
        if not site[0] in existent_sites:
            portal.portal_pingtool.invokeFactory(id = site[0], type_name = "PingInfo", title = site[1], url = site[2])

def removeConfiglet(self):
    if self.readDataFile('%s-uninstall.txt' % PROJECTNAME) is None:
        return
    portal_conf=getToolByName(self.getSite(),'portal_controlpanel')
    portal_conf.unregisterConfiglet('portal_pingtool')
