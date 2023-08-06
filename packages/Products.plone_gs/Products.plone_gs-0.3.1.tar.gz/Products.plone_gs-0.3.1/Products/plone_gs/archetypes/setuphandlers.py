from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.ZCatalog.exportimport import ZCatalogXMLAdapter
from Products.CMFCore.utils import getToolByName

class UIDCatalogXMLAdapter(ZCatalogXMLAdapter):
    name = 'uid_catalog'

def importUIDCatalog(context):
    """Import Archetypes UID catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'uid_catalog')
    importObjects(tool, '', context)

def exportUIDCatalog(context):
    """Export Archetypes UID catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'uid_catalog', None)
    if tool is None:
        return
    exportObjects(tool, '', context)

class ReferenceCatalogXMLAdapter(ZCatalogXMLAdapter):
    name = 'reference_catalog'

def importReferenceCatalog(context):
    """Import Archetypes Reference catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'reference_catalog')
    importObjects(tool, '', context)

def exportReferenceCatalog(context):
    """Export Archetypes Reference catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'reference_catalog', None)
    if tool is None:
        return
    exportObjects(tool, '', context)
