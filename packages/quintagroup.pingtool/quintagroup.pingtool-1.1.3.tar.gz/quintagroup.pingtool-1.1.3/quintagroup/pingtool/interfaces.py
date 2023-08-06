from zope.interface import Interface

class IPingTool(Interface):
    """ Interface for PingTool.
    """

class ICanonicalURL(Interface):
    """ Interface for canonical URL API providing."""

    def getCanonicalURL():
        """Get canonical_url property value."""

class ISyndicationObject(Interface):
    """ Interface for Syndicaion providing."""
