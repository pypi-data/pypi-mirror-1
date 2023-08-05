from Acquisition import aq_base
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.CMFPlone.utils import getToolByName


def setupVarious(context):
    site = context.getSite()
    # Only run step if a flag file is present
    if context.readDataFile('collective.editskinswitcher-various.txt') is None:
        return
    logger = context.getLogger('collective.editskinswitcher')
    logger.info('collective.editskinswitcher_various: Set Access Rule')
    set_access_rule(context, logger)
    return


def set_access_rule(context, logger):
    """Set the site access rule to the External Method `switchskin`.
    """
    site = context.getSite()
    if not 'switchskin' in site.objectIds():
        logger.info('collective.editskinswitcher_various: Switchskin not found. Adding it.')
        manage_addExternalMethod(site, 'switchskin', 'switchskin',
                                      'collective.editskinswitcher.switchskin',
                                      'switch_skin')
        site.manage_addProduct['SiteAccess'].manage_addAccessRule('switchskin')
        logger.info('collective.editskinswitcher_various: Access Rule is set.')
    return
