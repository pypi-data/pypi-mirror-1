from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName
from Products.CMFCalendar.CalendarTool import CalendarTool

from Products.plone_gs.utils import patchClassAsPropertyManager
    
#
# XXX: The following code should be in Products.ATContentTypes
#
_PROPERTIES = (
    {'id': 'calendar_types', 'type': 'lines', 'mode': 'w'},
    {'id': 'calendar_states', 'type': 'lines', 'mode': 'w'},
    {'id': 'use_session', 'type': 'boolean', 'mode': 'w'},
)

patchClassAsPropertyManager(CalendarTool, _PROPERTIES)

class CalendarToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for CMFCalendar tool.

    <object name="portal_calendar" meta_type="CMF Calendar Tool">
     <property name="calendar_types">
      <element value="TYPENAME">
      ...
     </property>
     <property name="calendar_states">
      <element value="STATE">
      ...
     </property>
     <property name="use_session">SIMPLE VALUE</property>
    </object>
    """
    _LOGGER_ID = 'Calendar.tool'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('Tool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self._initProperties(node)
        self._logger.info('Tool imported.')

def importCalendarTool(context):
    """Import CMFCalendar tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_calendar')
    importObjects(tool, '', context)

def exportCalendarTool(context):
    """Export CMFCalendar tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_calendar', None)
    if tool is None:
        return
    exportObjects(tool, '', context)
