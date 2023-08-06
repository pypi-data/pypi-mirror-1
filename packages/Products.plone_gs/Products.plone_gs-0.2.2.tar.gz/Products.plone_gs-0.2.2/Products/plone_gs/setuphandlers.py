from Products.CMFCore.utils import getToolByName

_INSTALLED_FROM_GS_BASELINE_PROFILE = [
    'Archetypes',
    'ATContentTypes',
    'ATReferenceBrowserWidget',
    'CMFCalendar',
    'CMFActionIcons',
    'CMFFormController',
    'CMFPlacefulWorkflow',
    'GroupUserFolder',
    'Marshall',
    'MimetypesRegistry',
    'PasswordResetTool',
    'PlonePAS',
    'PortalTransforms',
    'ResourceRegistries',
    'kupu',
]

def notifyQI(import_context):
    """ Notify QuickInstaller of pre-installed Products
    """
    portal = import_context.getSite()
    qi = getToolByName(portal, 'portal_quickinstaller')

    for product_name in _INSTALLED_FROM_GS_BASELINE_PROFILE:
        version = qi.getProductVersion(product_name)
        qi.notifyInstalled(product_name, installedversion=version, locked=True)
