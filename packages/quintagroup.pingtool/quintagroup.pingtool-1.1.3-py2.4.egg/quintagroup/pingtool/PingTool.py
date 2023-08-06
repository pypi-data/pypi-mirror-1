import os
from Acquisition import aq_base
from zLOG import LOG
from zope.interface import implements
from zope.component import getAdapter
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlone.interfaces.OrderedContainer import IOrderedContainer
from Products.CMFPlone.PloneFolder import PloneFolder
from Products.XMLRPCMethod.XMLRPCMethod import RPCThread, XMLRPCMethod

from quintagroup.pingtool import PingToolMessageFactory as _
from interfaces import IPingTool, ICanonicalURL
from config import PROJECTNAME


class PingTool(ATFolder, PloneFolder):
    """

    >>> IPingTool.implementedBy(PingTool)
    True
    """
    security = ClassSecurityInfo()

    implements(IPingTool)
    __implements__ = (IOrderedContainer,)

    archetype_name = portal_type = 'PingTool'
    manage_options =  (
            {'label' : 'Overview', 'action' : 'manage_overview'},
        ) + ATFolder.manage_options

    manage_overview = PageTemplateFile(os.path.join('www', 'overview'), globals(), __name__='manage_overview')

    def om_icons(self):
        """ Checking on ZMI for canonical_url setting."""
        icons = ({'path':'misc_/%s/tool.gif' % PROJECTNAME \
                    ,'alt':self.meta_type \
                    ,'title':self.meta_type \
                },)
        if not getAdapter(self, ICanonicalURL, 'canonical_url_adapter').getCanonicalURL():
            icons = icons + ({'path':'misc_/PageTemplates/exclamation.gif' \
                             ,'alt':'Error' \
                                ,'title':'PingTool needs setting canonical_url' \
                                },)
        return icons

    security.declareProtected(ManagePortal, 'pingFeedReader')
    def pingFeedReader(self,context):
        """ ping """
        message = {'portal_message': '', 'return_message': ''}
        status = 'failed'
        pingProp = self.getPingProperties(context)
    	if not pingProp['enable_ping']:
    	    message['portal_message'] = _(u'Ping is dissabled.')
    	    return status, message
        canonical_url = getAdapter(self, ICanonicalURL, 'canonical_url_adapter').getCanonicalURL()
        if not canonical_url:
            message['portal_message'] = _(u'Ping is impossible.Setup canonical_url.')
            return status, message
        sites = pingProp['ping_sites']
        message['portal_message'] = _(u'Select servers.')
        for site in sites:
            status = 'success'
            message['portal_message'] = _(u'The servers are pinged.')
            site_obj = getattr(self, site)
            site_method = site_obj.getMethod_name()
            site_url = site_obj.getUrl()
            PingMethod = XMLRPCMethod('myid', "", site_url, site_method, 25)
            title = context.Title()
            rss_version = site_obj.getRss_version()
            ping_url = pingProp['ping_' + rss_version]
            try:
                severities = 0
                result_ping = PingMethod(title, ping_url)
                result = ', '.join([':'.join((k, str(v))) for k, v in result_ping.items()])
            except:
                severities = 100
                result = 'The site %s generated error for %s.' % (site_url, ping_url)
            LOG(PROJECTNAME, severities, result)
            message['return_message'] += '\nReturned message from %s: %s' % (site_url, str(result))
        return status, message

    security.declareProtected(ManagePortal, 'getPingProperties')
    def getPingProperties(self, context):
        """ """
        obj=context
        pingProperties={}
        pingProperties['ping_sites'] = obj.getField('ping_sites').getAccessor(obj)()
        pingProperties['enable_ping'] = obj.getField('enable_ping').getAccessor(obj)()
        pingProperties['ping_Weblog'] = obj.getField('ping_Weblog').getAccessor(obj)()
        pingProperties['ping_RSS'] = obj.getField('ping_RSS').getAccessor(obj)()
        pingProperties['ping_RSS2'] = obj.getField('ping_RSS2').getAccessor(obj)()
        return  pingProperties

registerType(PingTool, PROJECTNAME)
