from persistent.mapping import PersistentMapping
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.Transform import Transform
from Products.PortalTransforms.chain import TransformsChain
from Products.MimetypesRegistry.common import MimeTypeException

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
