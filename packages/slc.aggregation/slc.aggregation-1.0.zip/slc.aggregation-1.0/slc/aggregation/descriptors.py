from zope import interface
from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
from slc.aggregation import interfaces

class AggregatorDescriptor(object):
    """ A descriptor for the Aggregator subtype.
    """
    interface.implements(IPortalTypedFolderishDescriptor)
    title = u'Aggregator'
    description = u''
    type_interface = interfaces.IAggregator
    for_portal_type = 'Folder'

