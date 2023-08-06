from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName

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
