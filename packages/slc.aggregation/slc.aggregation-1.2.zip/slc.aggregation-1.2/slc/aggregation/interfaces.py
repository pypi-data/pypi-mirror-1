from zope import interface

from zope.app.content.interfaces import IContentType 

class IAggregator(interface.Interface):
    """For the Aggregator subtype."""

interface.alsoProvides(IAggregator, IContentType)
