from Products.CMFCore.utils import getToolByName

class CanonicalURL(object):
    """ CanonicalURL adapter
    """

    def __init__(self, context):
        """ init
        """
        self.context = context

    def getCanonicalURL(self):
        """Get canonical_url property value
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.getProperty('canonical_url',None)
