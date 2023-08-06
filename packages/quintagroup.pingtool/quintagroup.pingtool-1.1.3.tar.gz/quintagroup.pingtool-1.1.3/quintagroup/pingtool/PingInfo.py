from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFDefault.utils import _dtmldir
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

from config import RSS_LIST, PROJECTNAME
from quintagroup.pingtool import PingToolMessageFactory as _

PingInfoSchema =  ATContentTypeSchema.copy() +  Schema((
    TextField('description',
        default='',
        searchable=False,
        widget=TextAreaWidget(
            label=_(
                u'label_description',
                default=u'Description'),
            description=_(
                u'help_description',
                default=u'Description of ping info'),
        ),
    ),
    StringField('url',
        default='',
        required=1,
        searchable=False,
        widget=StringWidget(
            label=_(
                u'label_url',
                default=u'Url ping servies'),
            description=_(
                u'help_url',
                default=u''),
        ),
    ),
    StringField('method_name',
        default='weblogUpdates.ping',
        required=1,
        searchable=False,
        widget=StringWidget(
            label=_(
                u'label_method_name',
                default=u'Method name'),
            description=_(
                u'help_method_name',
                default=u''),
        ),
    ),
    StringField('rss_version',
        default='Weblog',
        searchable=False,
	vocabulary=RSS_LIST,
        widget=SelectionWidget(
            label=_(
                u'label_rss_version',
                default=u'RSS version'),
            description=_(
                u'help_rss_version',
                default=u''),
        ),
    ),
),marshall=RFC822Marshaller())


class PingInfo(ATCTContent, HistoryAwareMixin):
    """Ping Info container
       id - name of the server to ping
       url - server ping url
       method_name - ping method
       rss_version - rss version supported by the server
    """
    __implements__ = (ATCTContent.__implements__,
                      HistoryAwareMixin.__implements__,
                     )
    schema = PingInfoSchema

    """Added some support of DublinCore"""
    security = ClassSecurityInfo()

    def Contributors(self):
        return self.contributors

    security.declareProtected(ModifyPortalContent, 'manage_metadata')
    manage_metadata = DTMLFile('zmi_metadata', _dtmldir)


registerType(PingInfo, PROJECTNAME)
