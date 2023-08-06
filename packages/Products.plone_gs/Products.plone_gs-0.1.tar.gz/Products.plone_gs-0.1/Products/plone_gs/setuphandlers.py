
from persistent.mapping import PersistentMapping

from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.ZCatalog.exportimport import ZCatalogXMLAdapter
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin
from Products.PortalTransforms.Transform import Transform
from Products.PortalTransforms.chain import TransformsChain
from Products.MimetypesRegistry.common import MimeTypeException


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

#
# XXX: The following code should already be in the Archetypes GS support stuff.
#
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

#
# XXX: The following code should be in Products.ATContentTypes
#
class ATCTToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for ATContentTypes tool.

    <object name="portal_atct" meta_type="ATCT Tool">
     <version value="x.y.z"/>
     <property name="xxx">SIMPLE VALUE</property>
     <property name="yyy">
      <element value="SIMPLE VALUE">
      ...
     </property>
     ...
    </object>
    """
    _LOGGER_ID = 'ATCT.tool'

    def _extractVersion(self):
        version_numeric, version_text = self.context.getVersion() 
        node = self._doc.createElement('version')
        node.setAttribute('value', version_text)
        return node

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractVersion())
        node.appendChild(self._extractProperties())

        self._logger.info('Tool exported.')
        return node

    def _initVersion(self, node):
        version = None
        for child in node.childNodes:
            if child.nodeName != 'version':
                continue
            version = str(child.getAttribute('value'))
            break
        if version:
            self.context.setInstanceVersion(version)
        else:
            self.context.setVersionFromFS()

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self._initVersion(node)

        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        self._logger.info('Tool imported.')

def importATCTTool(context):
    """Import ATContentTypes tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_atct')
    importObjects(tool, '', context)

def exportATCTTool(context):
    """Export ATContentTypes tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_atct', None)
    if tool is None:
        return
    exportObjects(tool, '', context)

#
# XXX: The following code should be in Products.MimetypesRegistry
#
class MimetypesRegistryXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for MimetypesRegistry tool.

    <object name="mimetypes_registry" meta_type="MimeTypes Registry">
     <property name="xxx">SIMPLE VALUE</property>
     <property name="yyy">
      <element value="SIMPLE VALUE">
      ...
     </property>
     ...
     <item>
      <mimetype value="major/minor"/>
      ...
      <extension value="foo"/>
      ...
      <glob value="bar*"/>
     </item>
     ...
     <encoding key="baz" value="bam"/>
     ...
     <suffix key="qux" value="qux.splif"/>
     ...
    </object>
    """
    _LOGGER_ID = 'MimetypesRegistry.tool'

    def _extractMimetypes(self):
        fragment = self._doc.createDocumentFragment()
        for item in self.context.mimetypes():
            node = self._doc.createElement('item')
            node.setAttribute('name', item.name())
            for mimetype in item.mimetypes:
                sub = self._doc.createElement('mimetype')
                sub.setAttribute('value', mimetype)
                node.appendChild(sub)
            for extension in item.extensions:
                sub = self._doc.createElement('extension')
                sub.setAttribute('value', extension)
                node.appendChild(sub)
            binary = getattr(item, 'binary', None)
            if binary is not None:
                sub = self._doc.createElement('binary')
                sub.setAttribute('value', binary and 'True' or 'False')
                node.appendChild(sub)
            icon_path = getattr(item, 'icon_path', None)
            if icon_path is not None:
                sub = self._doc.createElement('icon_path')
                sub.setAttribute('value', icon_path)
                node.appendChild(sub)
            for glob in item.globs:
                sub = self._doc.createElement('glob')
                sub.setAttribute('value', glob)
                node.appendChild(sub)
            fragment.appendChild(node)
        return fragment

    def _extractEncodingsMap(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in self.context.encodings_map.items():
            node = self._doc.createElement('encoding')
            node.setAttribute('key', key)
            node.setAttribute('value', value)
            fragment.appendChild(node)
        return fragment

    def _extractSuffixMap(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in self.context.suffix_map.items():
            node = self._doc.createElement('suffix')
            node.setAttribute('key', key)
            node.setAttribute('value', value)
            fragment.appendChild(node)
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractMimetypes())
        node.appendChild(self._extractEncodingsMap())
        node.appendChild(self._extractSuffixMap())

        self._logger.info('Tool exported.')
        return node

    def _purgeMimetypes(self):
        mtr = self.context
        mtr._mimetypes.clear()
        mtr.extensions.clear()
        mtr.globs.clear()

    def _purgeEncodingsMap(self):
        self.context.encodings_map.clear()

    def _purgeSuffixesMap(self):
        self.context.suffix_map.clear()

    def _initMimetypes(self, node):
        from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
        for item in node.childNodes:
            if item.nodeName != 'item':
                continue
            name = str(item.getAttribute('name'))
            mimetypes = []
            extensions = []
            globs = []
            icon_path = None
            binary = None
            for child in item.childNodes:
                if child.nodeName == 'mimetype':
                    value = child.getAttribute('value')
                    mimetypes.append(value)
                elif child.nodeName == 'extension':
                    value = child.getAttribute('value')
                    extensions.append(value)
                elif child.nodeName == 'glob':
                    value = child.getAttribute('value')
                    globs.append(value)
                elif child.nodeName == 'binary':
                    value = child.getAttribute('value')
                    binary = value.lower() in ('true', 'yes')
                elif child.nodeName == 'icon':
                    value = child.getAttribute('value')
                    icon_path = value
            item = MimeTypeItem(name, mimetypes, extensions or None,
                                binary, icon_path, globs or None)
            self.context.register(item)

    def _initEncodingsMap(self, node):
        encodings_map = self.context.encodings_map.copy()
        found = False
        for child in node.childNodes:
            if child.nodeName != 'encoding':
                continue
            found = True
            key = child.getAttribute('key')
            value = child.getAttribute('value')
            encodings_map[key] = value
        if found:
            self.context.encodings_map = encodings_map

    def _initSuffixesMap(self, node):
        suffix_map = self.context.suffix_map.copy()
        found = False
        for child in node.childNodes:
            if child.nodeName != 'suffix':
                continue
            found = True
            key = child.getAttribute('key')
            value = child.getAttribute('value')
            suffix_map[key] = value
        if found:
            self.context.suffix_map = suffix_map

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeMimetypes()
            self._purgeEncodingsMap()
            self._purgeSuffixesMap()

        self._initProperties(node)
        self._initMimetypes(node)
        self._initEncodingsMap(node)
        self._initSuffixesMap(node)

        self._logger.info('Tool imported.')

def importMimetypesRegistry(context):
    """Import MimetypesRegistry tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'mimetypes_registry')
    importObjects(tool, '', context)

def exportMimetypesRegistry(context):
    """Export MimetypesRegistry tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'mimetypes_registry', None)
    if tool is None:
        return
    exportObjects(tool, '', context)

#
# XXX: The following code should be in Products.PortalTransforms
#
class PortalTransformsToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for ATContentTypes tool.

    <object name="portal_atct" meta_type="ATCT Tool">
     <property name="xxx">SIMPLE VALUE</property>
     <property name="yyy">
      <element value="SIMPLE VALUE">
      ...
     </property>
     ...
     <transform name="abc" module="foo.bar.doBaz"/>
     ...
     <chain name="pqr" transforms="abc def ghi"/>
     ...
     <mimetype input="foo/bar">
      <target output="baz/bam" name="abc"/>
      ...
     </mimetype>
     ...
     <policy output="baz/bam" transforms="def ghi"/>
     ...
    </object>
    """
    _LOGGER_ID = 'PortalTransforms.tool'

    def _extractMTMap(self):
        fragment = self._doc.createDocumentFragment()
        for input_mt, segments in sorted(self.context._mtmap.items()):
            node = self._doc.createElement('mimetype')
            node.setAttribute('input', input_mt)
            for output_mt, transforms in segments.items():
                sub = self._doc.createElement('target')
                sub.setAttribute('output', output_mt)
                t_ids = [x.id for x in transforms]
                sub.setAttribute('transforms', ' '.join(t_ids))
                node.appendChild(sub)
            fragment.appendChild(node)
        return fragment

    def _extractPolicies(self):
        fragment = self._doc.createDocumentFragment()
        for output_mt, required in sorted(self.context.listPolicies()):
            node = self._doc.createElement('policy')
            node.setAttribute('output', output_mt)
            node.setAttribute('requirement', ' '.join(requirements))
            fragment.appendChild(node)
        return fragment

    def _extractTransforms(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in sorted(self.context.objectItems('Transform')):
            node = self._doc.createElement('transform')
            node.setAttribute('name', key)
            node.setAttribute('module', value.module)
            fragment.appendChild(node)
        return fragment

    def _extractChains(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in sorted(self.context.objectItems('TransformsChain')):
            node = self._doc.createElement('chain')
            node.setAttribute('name', key)
            node.setAttribute('transforms', ' '.join(value._object_ids))
            fragment.appendChild(node)
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractTransforms())
        node.appendChild(self._extractChains())
        node.appendChild(self._extractMTMap())
        node.appendChild(self._extractPolicies())

        self._logger.info('Tool exported.')
        return node

    def _purgeMTMap(self):
        self.context._mtmap = PersistentMapping()

    def _purgePolicies(self):
        self.context._policies = PersistentMapping()

    def _purgeTransforms(self):
        t_ids = self.context.objectIds('Transform')
        self.context.manage_delObjects(t_ids)

    def _purgeChains(self):
        tc_ids = self.context.objectIds('TransformChains')
        self.context.manage_delObjects(tc_ids)

    def _initTransforms(self, node):
        for child in node.childNodes:
            if child.nodeName == 'transform':
                name = child.getAttribute('name')
                module = child.getAttribute('module')
                transform = Transform(name, module)
                self.context._setObject(str(name), transform)
                try:
                    self.context._mapTransform(transform)
                except MimeTypeException:
                    # don't choke on broken transforms
                    pass

    def _initChains(self, node):
        for child in node.childNodes:
            if child.nodeName == 'chain':
                name = child.getAttribute('name')
                description = '' # should be in XML
                transforms = child.getAttribute('transforms').split()
                chain = TransformsChain(id, description, transforms)
                self.context._setObject(id, chain)
                self.context._mapTransform(transform)

    def _initMTMap(self, node):
        # This should be handled by the '_mapTransform' call above.
        pass

    def _initPolicies(self, node):
        for child in node.childNodes:
            if child.nodeName == 'policy':
                output = child.getAttribute('output')
                required = child.getAttribute('transforms').split()
                self.context.manage_addPolicy(output, transforms)

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeMTMap()
            self._purgePolicies()
            self._purgeTransforms()
            self._purgeChains()

        self._initProperties(node)
        self._initTransforms(node)
        self._initChains(node)
        self._initPolicies(node)
        self._initMTMap(node)

        self._logger.info('Tool imported.')

def importPortalTransformsTool(context):
    """Import PortalTransforms tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_transforms')
    importObjects(tool, '', context)

def exportPortalTransformsTool(context):
    """Export PortalTransforms tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_transforms', None)
    if tool is None:
        return
    exportObjects(tool, '', context)


# PlonePAS has a UserFactory plugin which doesn't have a distinct interface.
class IPloneUserFactoryPlugin(IUserFactoryPlugin):
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
