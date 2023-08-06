# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.22 $
from AccessControl import ClassSecurityInfo
import Globals
import zLOG
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from helpers import add_and_edit

class WidgetRegistry(SimpleItem):
    security = ClassSecurityInfo()

    meta_type = "XMLWidgets Registry"

    manage_options = (
        {'label':'Info', 'action':'info_tab'},
        ) + SimpleItem.manage_options

    info_tab = PageTemplateFile(
        'www/widgetRegistryInfoTab',
        globals(),  __name__='info_tab')

    # needed, as this uses here/manage_page_header
    # which need the "manager" role
    security.declareProtected('View management screens', 'info_tab')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._node_map = {}
        self._allowed_map = {}
        self._display_map = {}
        
    security.declareProtected('Change XMLWidgets Registries',
                              'addWidget')
    def addWidget(self, nodeName, widget_path):
        self._node_map[nodeName] = widget_path
        self._node_map = self._node_map

    security.declareProtected('Change XMLWidgets Registries',
                              'clearWidgets')
    def clearWidgets(self):
        """Clear all widgets.
        """
        self._node_map = {}
        self._allowed_map = {}
        self._display_map = {}

    security.declareProtected('Change XMLWidgets Registries',
                              'setAllowed')
    def setAllowed(self, nodeName, allowed):
        """Set which names can be inserted in another node.
        """
        self._allowed_map[nodeName] = allowed
        self._allowed_map = self._allowed_map

    security.declareProtected('Change XMLWidgets Registries',
                              'setDisplayName')
    def setDisplayName(self, nodeName, displayName):
        """Set visible name for a nodeName.
        """
        self._display_map[nodeName] = displayName
        self._display_map = self._display_map
    
    security.declareProtected('View', 'findWidget')
    def findWidget(self, node):
        widget_path = self._node_map.get(node.nodeName, None)
        if widget_path is None:
            zLOG.LOG('XMLWidgets',zLOG.ERROR,
                     '%s: no view widget registered for node %s' % \
                     (self.getId(), node.nodeName))
            return None        
        return widget_path

    security.declareProtected('View', 'getWidget')
    def getWidget(self, node):
        widget_path = self._node_map.get(node.nodeName, None)
        if widget_path is None:
            raise AttributeError, ('%s: no widget registered for node name %s' %\
                                   (self.getId(), node.nodeName))
        obj = self.aq_inner
        for step in widget_path:
            obj = getattr(obj, step, None)
            if obj is None:
                raise AttributeError, \
                      ('XML Widget registry %s cannot acquire %s ("%s" not found)' % \
                       ( self.getId(), '/'.join(widget_path), step ))
        self.REQUEST['node'] = node
        return obj
    
    security.declareProtected('View', 'getDisplayName')
    def getDisplayName(self, nodeName):
        """Get the list of nodes allowed in nodeName.
        """
        return self._display_map.get(nodeName, nodeName)
    
    security.declareProtected('View', 'isAllowed')
    def isAllowed(self, parentName, name):
        """Check whether we are allowed in parentName.
        """
        return name in self._allowed_map.get(parentName, [])

    security.declareProtected('View', 'getAllowed')
    def getAllowed(self, parentName):
        """Give list of what is allowed in this parent.
        """
        return self._allowed_map.get(parentName, [])
    
Globals.InitializeClass(WidgetRegistry)

manage_addWidgetRegistryForm = PageTemplateFile(
    "www/widgetRegistryAdd", globals(),
    __name__='manage_addWidgetRegistryForm')

def manage_addWidgetRegistry(self, id, title="", REQUEST=None):
    """Add widget registry to folder.
    """
    # add actual object
    id = self._setObject(id, WidgetRegistry(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
