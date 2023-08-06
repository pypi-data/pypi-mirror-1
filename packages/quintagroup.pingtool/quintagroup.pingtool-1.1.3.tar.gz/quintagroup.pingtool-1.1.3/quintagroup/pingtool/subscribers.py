from zope.interface import alsoProvides, noLongerProvides
from zope.component import getUtility

from interfaces import ISyndicationObject

try:
    from vice.outbound.interfaces import IFeedConfigs
    success = True
except ImportError:
    success = False

def mark_syndication(object, event):
    if hasattr(object.aq_base, 'syndication_information') or \
               (success and IFeedConfigs(object.aq_base, None)) and IFeedConfigs(object.aq_base).enabled:
        if not ISyndicationObject.providedBy(object):
            alsoProvides(object, ISyndicationObject)
    else:
        if ISyndicationObject.providedBy(object):
            noLongerProvides(object, ISyndicationObject)
