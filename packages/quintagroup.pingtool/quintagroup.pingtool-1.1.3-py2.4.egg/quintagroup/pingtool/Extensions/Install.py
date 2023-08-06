from zope.component import getSiteManager

from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
ADAPTERNAMES = ('pingtool_extender', 'canonical_url_adapter', '')

def uninstall_componentRegistryAdapter(self, ADAPTERNAME):
        sm = getSiteManager(self)

        registrations = tuple(sm.registeredAdapters())
        for registration in registrations:
            if registration.name == ADAPTERNAME:
                factory = registration.factory
                required = registration.required
                provided = registration.provided
                name = registration.name
                sm.unregisterAdapter(factory=factory,
                                           required=required,
                                           provided=provided,
                                           name=name)

def uninstall(self):
    out = StringIO()
    for ADAPTERNAME in ADAPTERNAMES:
        uninstall_componentRegistryAdapter(self, ADAPTERNAME)
        print >> out, "\nSuccessfully uninstalled %s adapter." % ADAPTERNAME
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-quintagroup.pingtool:uninstall')
    print >> out, "Imported uninstall profile."
    return out.getvalue()
