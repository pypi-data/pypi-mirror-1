import logging
import transaction
from Products.CMFCore.utils import getToolByName
from config import DEPENDENCIES

log = logging.getLogger("slc.autotranslate/setuphandlers.py")

def isNotPublicationsProfile(self):
    return self.readDataFile('slc_autotranslate_marker.txt') is None

def installDependencies(self):
    """ Install product dependencies
    """
    if isNotPublicationsProfile(self):
        return
    log.info("installDependencies")
    site = self.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if not qi.isProductInstalled(product):
            log.info("Installing dependency: %s" % product)
            qi.installProduct(product)
            transaction.savepoint()

