# base test case classes
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

# These must install cleanly, ZopeTestCase will take care of the others
ztc.installProduct('CMFSin')
ztc.installProduct('PressRoom')
ztc.installProduct('LinguaPlone')
ztc.installProduct('slc.aggregation')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['LinguaPlone', 'slc.aggregation']

ptc.setupPloneSite(products=PRODUCTS)

class AggregationTestCase(ptc.PloneTestCase):
    """Base class for integration tests. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
