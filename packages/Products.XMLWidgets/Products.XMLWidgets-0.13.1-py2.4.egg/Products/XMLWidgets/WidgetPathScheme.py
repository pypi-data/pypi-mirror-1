# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
from Products.ParsedXML.NodePath.ElementIdPath import ElementIdPathScheme
from WidgetDOM import getWidgetWrappedNode

class WidgetPathScheme(ElementIdPathScheme):
    def resolve_steps(self, top_node, steps):
        top_node = getWidgetWrappedNode(top_node)
        return ElementIdPathScheme.resolve_steps(
            self, top_node, steps)
    
