from persistent.mapping import PersistentMapping
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.MetadataTool import MetadataTool

from Products.plone_gs.utils import patchClassAsPropertyManager
    
#
# XXX: The following code should be in Products.CMFDefault
#
_PROPERTIES = (
    {'id': 'publisher', 'type': 'string', 'mode': 'w'},
)

patchClassAsPropertyManager(MetadataTool, _PROPERTIES)
    
class MetadataToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for CMFDefault's Metadata tool.

    <object name="portal_metadata" meta_type="CMF Metadata Tool">
     <property name="publisher">PUBLISHER</property>
     ...
     <element name="ELEMENT" multivalued="FALSE">
      <policy typename="TYPENAME" required="True" supply_default="True"
              enforce_vocabulary="True">
       <default value="VALUE"/>
       ... # only if element is multi-valued
       <allowed value="TERM"/>
      </policy>
     </element>
    </object>
    """
    _LOGGER_ID = 'Metadata.tool'

    def _extractPolicies(self):
        def _b(x):
            return x and 'True' or 'False'
        def _n(x):
            if x is None:
                return ''
            return x
        fragment = self._doc.createDocumentFragment()
        for element, spec in self.context.listElementSpecs():
            mv = spec.isMultiValued()
            node = self._doc.createElement('element')
            node.setAttribute('name', element)
            node.setAttribute('multivalued', _b(mv))
            for typename, policy in spec.listPolicies():
                sub = self._doc.createElement('policy')
                sub.setAttribute('typename', _n(typename))
                sub.setAttribute('required', _b(policy.isRequired()))
                sub.setAttribute('supply_default', _b(policy.supplyDefault()))
                sub.setAttribute('enforce_vocabulary',
                                 _b(policy.enforceVocabulary()))

                if not mv:
                    defaults = [policy.defaultValue()]
                else:
                    defaults = policy.defaultValue()
                for value in defaults:
                    dv = self._doc.createElement('default')
                    dv.setAttribute('value', value)
                    sub.appendChild(dv)

                for value in policy.allowedVocabulary():
                    av = self._doc.createElement('allowed')
                    av.setAttribute('value', value)
                    sub.appendChild(av)

                node.appendChild(sub)
            fragment.appendChild(node)
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractPolicies())

        self._logger.info('Tool exported.')
        return node

    def _purgePolicies(self):
        self.context.element_specs = PersistentMapping()

    def _initPolicies(self, node):
        def _b(x):
            return x.lower() in ('true', 'yes')

        for child in node.childNodes:
            if child.nodeName != 'element':
                continue
            element = str(child.getAttribute('name'))
            mv = _b(child.getAttribute('multivalued'))

            self.context.addElementSpec(element, mv)

            for grand in child.childNodes:
                defaults = []
                allowed = []
                typename = str(child.getAttribute('typename')) or None
                required = _b(child.getAttribute('required'))
                supply_default = _b(child.getAttribute('supply_default'))
                enforce_vocabulary = _b(child.getAttribute(
                                                    'enforce_vocabulary'))
                for ggrand in grand.childNodes:
                    if ggrand.nodeName == 'default':
                        defaults.append(str(ggrand.getAttribute('value')))
                    elif ggrand.nodeName == 'allowed':
                        allowed.append(str(ggrand.getAttribute('value')))

                if not mv:
                    if defaults:
                        default = defaults[0]
                    else:
                        default = ''
                else:
                    default = defaults

                if typename is None:
                    self.context.updateElementPolicy(element,
                                                     typename,
                                                     required,
                                                     supply_default,
                                                     default,
                                                     enforce_vocabulary,
                                                     allowed)
                else:
                    self.context.addElementPolicy(element,
                                                  typename,
                                                  required,
                                                  supply_default,
                                                  default,
                                                  enforce_vocabulary,
                                                  allowed)

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgePolicies()

        self._initProperties(node)
        self._initPolicies(node)
        self._logger.info('Tool imported.')

def importMetadataTool(context):
    """Import CMFDefault's Metadata tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_metadata')
    importObjects(tool, '', context)

def exportMetadataTool(context):
    """Export CMFDefault's Metadata tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_metadata', None)
    if tool is None:
        return
    exportObjects(tool, '', context)
