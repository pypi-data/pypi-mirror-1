from zope.interface import Interface

class IContentGenerator(Interface):
    """The main interface to accessing the content generator.
    """

class IPloneContentGenerator(IContentGenerator):
    """A plone content generator."""

class IContentSniffer(Interface):
    """An interface to sniff content."""

class IZopeContentSniffer(IContentSniffer):
    """An interface to sniff zope content."""
