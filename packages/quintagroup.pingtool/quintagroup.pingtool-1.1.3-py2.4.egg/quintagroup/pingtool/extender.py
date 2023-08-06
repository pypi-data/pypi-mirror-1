from zope.component import getAdapter
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender.field import ExtensionField

from quintagroup.pingtool import PingToolMessageFactory as _
from interfaces import ICanonicalURL

def getPingDefaultUrl(context, rss_version='Weblog'):
    rss_templates = {'ping_Weblog':'', 'ping_RSS':'/RSS', 'ping_RSS2':'/RSS2'}
    url = getToolByName(context, 'portal_url').getRelativeContentURL(context)
    portal_pingtool = getToolByName(context, 'portal_pingtool', None)
    ping_url = ''
    if portal_pingtool:
        canonical_url = getAdapter(portal_pingtool, ICanonicalURL, 'canonical_url_adapter').getCanonicalURL()
        if canonical_url:
            if not canonical_url.endswith('/'):
                canonical_url += '/'
            if not canonical_url.startswith('http://'):
                canonical_url = 'http://' + canonical_url
            url = canonical_url + url
            site_rss_version = rss_templates[rss_version]
            ping_url = url + site_rss_version
    return ping_url


class MyLinesField(ExtensionField, LinesField):
    """A trivial lines field."""

class MyStringField(ExtensionField, StringField):
    """The string field with custom 'get' method."""

    def get(self, instance, **kwargs):
        value = super(MyStringField, self).get(instance)
        if not value:
            value = getPingDefaultUrl(instance, self.__name__)
        return value

class MyBooleanField(ExtensionField, BooleanField):
    """A trivial boolean field."""


class PingToolExtender(object):
    """ PingToolExtender custom field
    """

    fields = [
            MyBooleanField('enable_ping',
                default=0,
                schemata='PingSetup',
                widget=BooleanWidget(label=_(u'label_enable_ping', default=u'Enable Ping'),
                                       description=_(u'help_enable_ping',
                                       default=u''))),
            MyLinesField('ping_sites',
                schemata='PingSetup',
                multiValued=True,
                vocabulary_factory=u'quintagroup.pingtool.getPingSites',
                enforceVocabulary=True,
                size=10,
                widget=MultiSelectionWidget(format='checkbox',
                                    size=10,
                                    label=_(u'label_ping_sites', default=u'Ping Sites'),
                                    description=_(u'help_ping_sites',
                                    default=u'List of ping sites.'))),
            MyStringField('ping_Weblog',
                schemata='PingSetup',
                widget=StringWidget(label=_(u'label_weblog_rssversion', default=u'Ping url for Weblog'),
                                    description=_(u'help_weblog_rssversion',
                                    default=u'RSS version.'))),
            MyStringField('ping_RSS',
                schemata='PingSetup',
                widget=StringWidget(label=_(u'label_rss1_rssversion', default=u'Ping url for RSS'),
                                    description=_(u'help_rss1_rssversion',
                                    default=u'RSS version.'))),
            MyStringField('ping_RSS2',
                schemata='PingSetup',
                widget=StringWidget(label=_(u'label_rss2_rssversion', default=u'Ping url for RSS2'),
                                    description=_(u'help_rss2_rssversion',
                                    default=u'RSS version.'))),
             ]
                
    def __init__(self, context):
        self.context = context

    def getFields(self):
        return  self.fields
