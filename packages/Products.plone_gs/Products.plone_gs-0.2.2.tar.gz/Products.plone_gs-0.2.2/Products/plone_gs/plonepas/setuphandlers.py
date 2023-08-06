from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin

class IPloneUserFactoryPlugin(IUserFactoryPlugin):
    """ Provide a distinct interface for the PlonePAS user factory plugin.
    """
    pass

def importPAS(context):
    """ Trigger the PAS import.
    """
    site = context.getSite()
    tool = getToolByName(site, 'acl_users')
    if 'setup_tool' not in tool.objectIds():
        from Products.GenericSetup.tool import SetupTool
        tool._setObject('setup_tool', SetupTool('setup_tool'))
    setup_tool = tool.setup_tool
    setup_tool.setImportContext('profile-Products.plone_gs:pas')
    setup_tool.runAllImportSteps(purge_old=True)
