from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName

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
     <topic-index name="idx_name" title="Friendly" description="Desc"
                  enabled="True">
      <criterion name="name" description="description" />
     </topic-index>
     ...
     <topic-metadata name="idx_name" title="Friendly" description="Desc"
                  enabled="True" />
     ...
     <allowed type="typename"/>
     ...
    </object>
    """
    _LOGGER_ID = 'ATCT.tool'

    def _extractVersion(self):
        version_numeric, version_text = self.context.getVersion() 
        node = self._doc.createElement('version')
        node.setAttribute('value', version_text)
        return node

    def _extractTopicIndexes(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in sorted(self.context.topic_indexes.items()):
            node = self._doc.createElement('topic-index')
            node.setAttribute('name', key)
            node.setAttribute('title', value.friendlyName)
            node.setAttribute('description', value.description)
            node.setAttribute('enabled', value.enabled and 'True' or 'False')
            for criterion in value.criteria:
                sub = self._doc.createElement('criterion')
                sub.setAttribute('name', criterion)
                node.appendChild(sub)
            fragment.appendChild(node)
        return fragment

    def _extractTopicMetadata(self):
        fragment = self._doc.createDocumentFragment()
        for key, value in sorted(self.context.topic_metadata.items()):
            node = self._doc.createElement('topic-metadata')
            node.setAttribute('name', key)
            node.setAttribute('title', value.friendlyName)
            node.setAttribute('description', value.description)
            node.setAttribute('enabled', value.enabled and 'True' or 'False')
            fragment.appendChild(node)
        return fragment

    def _extractAllowedPortalTypes(self):
        fragment = self._doc.createDocumentFragment()
        for typename in sorted(self.context.allowed_portal_types):
            node = self._doc.createElement('allowed')
            node.setAttribute('type', typename)
            fragment.appendChild(node)
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractVersion())
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractTopicIndexes())
        node.appendChild(self._extractTopicMetadata())
        node.appendChild(self._extractAllowedPortalTypes())

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

    def _purgeTopicIndexes(self):
        self.context.topic_indexes = {}

    def _purgeTopicMetadata(self):
        self.context.topic_metadata = {}

    def _purgeAllowedPortalTypes(self):
        self.context.allowed_portal_types = []

    def _initTopicIndexes(self, node):
        for item in node.childNodes:
            if item.nodeName != 'topic-index':
                continue
            name = str(item.getAttribute('name'))
            title = str(item.getAttribute('title'))
            description = str(item.getAttribute('description'))
            enabled = str(item.getAttribute('enabled'))
            enabled = enabled.lower() in ('true', 'yes')
            criteria = []
            for child in item.childNodes:
                if child.nodeName == 'criterion':
                    cname = str(child.getAttribute('name'))
                    cdesc = str(child.getAttribute('description'))
                    criteria.append({'name': cname, 'description': cdesc})
            self.context.addIndex(name, title, description, enabled, criteria)

    def _initTopicMetadata(self, node):
        for item in node.childNodes:
            if item.nodeName != 'topic-metadata':
                continue
            name = str(item.getAttribute('name'))
            title = str(item.getAttribute('title'))
            description = str(item.getAttribute('description'))
            enabled = str(item.getAttribute('enabled'))
            enabled = enabled.lower() in ('true', 'yes')
            self.context.addMetadata(name, title, description, enabled)

    def _initAllowedPortalTypes(self, node):
        allowed = []
        for item in node.childNodes:
            if item.nodeName != 'allowed':
                continue
            allowed.append(str(item.getAttribute('type')))
        self.context.allowed_portal_types = allowed

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self._initVersion(node)

        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeTopicIndexes()
            self._purgeTopicMetadata()
            self._purgeAllowedPortalTypes()

        self._initProperties(node)
        self._initTopicIndexes(node)
        self._initTopicMetadata(node)
        self._initAllowedPortalTypes(node)

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
