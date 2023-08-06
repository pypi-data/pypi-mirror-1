import logging
import transaction
from Products.CMFCore.utils import getToolByName
from config import PRODUCT_DEPENDENCIES

log = logging.getLogger('slc.aggregation.setuphandlers.py')

def is_not_aggregation_profile(self):
    return self.readDataFile('slc_aggregation_marker.txt') is None

def install_dependencies(self):
    """ Install product dependencies
    """
    if is_not_aggregation_profile(self):
        return

    log.info("installDependencies")
    site = self.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in PRODUCT_DEPENDENCIES:
        if not qi.isProductInstalled(product):
            log.info("Installing dependency: %s" % product)
            qi.installProduct(product)
            transaction.savepoint(optimistic=True)
    transaction.commit()
