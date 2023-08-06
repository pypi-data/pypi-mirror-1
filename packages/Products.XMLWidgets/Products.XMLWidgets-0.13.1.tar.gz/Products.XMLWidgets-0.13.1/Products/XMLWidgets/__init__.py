# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.14 $
from Products.ParsedXML.NodePath import registry
from WidgetPathScheme import WidgetPathScheme
import WidgetRegistry
import EditorService

def initialize(context):
    context.registerClass(
        WidgetRegistry.WidgetRegistry,
        permission = "Add XMLWidget Registries",
        constructors = (WidgetRegistry.manage_addWidgetRegistryForm,
                        WidgetRegistry.manage_addWidgetRegistry),
        icon = "www/widget_service.gif"
        )
    
    context.registerClass(
        EditorService.EditorService,
        permission = "Add XMLWidget Registries",
        constructors = (EditorService.manage_addEditorServiceForm,
                        EditorService.manage_addEditorService),
        icon = "www/editor_service.gif"
        )

    registry.register_scheme(WidgetPathScheme('widget'))
