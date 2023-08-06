from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

class KupuLibraryToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for ATContentTypes tool.

    <object name="kupu_library_tool" meta_type="Kupu Library Tool">
     <library id="abc" title="TITLE"
              uri="http://example.com/kupu"
              src="http://example.com/kupu/src"
              icon="http://example.com/kupu/icon" />
     ...
     <resource type="foo" portal_types="def ghi"/>
     ...
    </object>
    """
    _LOGGER_ID = 'kupu.tool'

    def _getExpressionText(self, x):
        if isinstance(x, Expression):
            return x.text
        return x

    def _extractLibraries(self):
        fragment = self._doc.createDocumentFragment()
        for info in self.context._libraries:
            node = self._doc.createElement('library')
            node.setAttribute('id', info['id'])
            node.setAttribute('title', self._getExpressionText(info['title']))
            node.setAttribute('uri', self._getExpressionText(info['uri']))
            node.setAttribute('src', self._getExpressionText(info['src']))
            node.setAttribute('icon', self._getExpressionText(info['icon']))
            fragment.appendChild(node)
        return fragment

    def _extractResourceTypes(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in sorted(self.context._res_types.items()):
            node = self._doc.createElement('resource')
            node.setAttribute('type', key)
            node.setAttribute('portal_types', ','.join(value))
            fragment.appendChild(node)
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractLibraries())
        node.appendChild(self._extractResourceTypes())

        self._logger.info('Tool exported.')
        return node

    def _purgeLibraries(self):
        self.context._libraries = []

    def _purgeResourceTypes(self):
        self.context._res_types = {}

    def _initLibraries(self, node):
        for child in node.childNodes:
            if child.nodeName == 'library':
                id = child.getAttribute('id')
                title = child.getAttribute('title')
                uri = child.getAttribute('uri')
                src = child.getAttribute('src')
                icon = child.getAttribute('icon')
                self.context.addLibrary(id, title, uri, src, icon)

    def _initResourceTypes(self, node):
        for child in node.childNodes:
            if child.nodeName == 'resource':
                resource_type = child.getAttribute('type')
                portal_types = child.getAttribute('portal_types').split(',')
                self.context.addResourceType(resource_type, portal_types)


    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeLibraries()
            self._purgeResourceTypes()

        self._initLibraries(node)
        self._initResourceTypes(node)

        self._logger.info('Tool imported.')

def importKupuLibraryTool(context):
    """Import KupuLibrary tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'kupu_library_tool')
    importObjects(tool, '', context)

def exportKupuLibraryTool(context):
    """Export KupuLibrary tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'kupu_library_tool', None)
    if tool is None:
        return
    exportObjects(tool, '', context)

