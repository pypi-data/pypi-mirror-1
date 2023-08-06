# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.11 $
"""
XMLWidgets support for DOM classes.
"""

import Globals
import Acquisition
from Products.ParsedXML import DOMProxy, DOM, ExtraDOM
from Products.ParsedXML.ManageableDOM import DOMTraversable
import xml.dom
from Products.ParsedXML.NodePath import registry

class WidgetAttribute(Acquisition.Implicit):
    
    def __getitem__(self, name):
        """
        """
        node = self.aq_parent
        return getattr(
            self.service_editor.getWidget(node), name)
    
   # def __getitem__(self, name):
   #     """
   #     """
   #     node = self.aq_parent
   #     wr = getattr(self, node.getWidgetRegistryName())
   #     return getattr(wr.getWidget(node), name)

def getWidgetWrappedNode(node):
    """Get a node for the widget wrapped with the WidgetDOM wrappers.
    """
    if node is None:
        return
    wrapper_type = WRAPPER_TYPES[node._get_nodeType()]
    parent = node.getPersistentDoc() or node
    return wrapper_type(node._node,
                        node._persistentDoc).__of__(parent)

class WidgetWrapper:
    """
    Mixin class to go alongside WidgetNode classes.
    """

    # anything that returns subobjs must grant access to them
    __allow_access_to_unprotected_subobjects__ = 1

    def wrapNamedNodeMap(self, obj):
        if obj is None:
            return None
        parent = self.getPersistentDoc() or self
        wrapped = WidgetNamedNodeMap(obj, self._persistentDoc).__of__(parent)
        return wrapped
        
    def wrapNodeList(self, obj):
        parent = self.getPersistentDoc() or self
        wrapped = WidgetNodeList(obj, self._persistentDoc).__of__(parent)      
        return wrapped

    def wrapDOMObj(self, node):
        """Return the appropriate class wrapped around the node."""
        if node is None:
            return
        wrapper_type = WRAPPER_TYPES[node._get_nodeType()]
        parent = self.getPersistentDoc() or self
        wrapped = wrapper_type(node,
                               self._persistentDoc).__of__(parent)      
        return wrapped
    
    def getWidgetRegistryName(self):
        session = self.REQUEST.SESSION
        # get document url XXX arrggh horrible hacks
        node = self
        while getattr(node.aq_base, 'meta_type', None) != 'Parsed XML':
            node = node.aq_parent
        document_url = node.absolute_url()
        document = node
        
        if session.has_key('xmlwidgets_node_event_handler'):
            xmlwidgets_node_event_handler = session['xmlwidgets_node_event_handler']
        else:
            xmlwidgets_node_event_handler = {}

        nodepath_wr_names = xmlwidgets_node_event_handler.get(
            document_url, None)
        if nodepath_wr_names:
            node = self
            while node is not None:
                path = registry.create_path(node.ownerDocument, node, 'widget')
                name = nodepath_wr_names.get(path, None)
                if name:
                    return name
                node = node.parentNode

        # if we can't find any special registry, we fall back on
        # document editor for now XXX
        if not session.has_key('xmlwidgets_event_handler'):
            session['xmlwidgets_event_handler'] = {}
        result = session['xmlwidgets_event_handler'].get(
            document_url, 'service_document_editor')
        return result

    def getWidgetRegistryNode(self):
        session = self.REQUEST.SESSION
        # get document url XXX arrggh horrible hacks
        node = self
        while getattr(node.aq_base, 'meta_type', None) != 'Parsed XML':
            node = node.aq_parent
        document_url = node.absolute_url()
        
        if session.has_key('xmlwidgets_node_event_handler'):
            xmlwidgets_node_event_handler = session['xmlwidgets_node_event_handler']
        else:
            xmlwidgets_node_event_handler = {}

        nodepath_wr_names = xmlwidgets_node_event_handler.get(
            document_url, None)
        if nodepath_wr_names:
            node = self
            while node is not None:
                path = registry.create_path(node.ownerDocument, node, 'widget')
                name = nodepath_wr_names.get(path, None)
                if name:
                    return node
                node = node.parentNode

        # if we can't find any special registry, return document element node
        return document.documentElement

    edit = WidgetAttribute()

class WidgetTraversable(DOMTraversable):
    """Traversing the widget way.
    """
    pass

    
# According to DOM Erratum Core-14, the empty string should be
# accepted as equivalent to null for hasFeature().

_WIDGET_DOM_FEATURES = (
    ("org.zope.dom.persistence", None),
    ("org.zope.dom.persistence", ""),
    ("org.zope.dom.persistence", "1.0"),
    ("org.zope.dom.acquisition", None),
    ("org.zope.dom.acquisition", ""),
    ("org.zope.dom.acquisition", "1.0"),
    )

_WIDGET_DOM_NON_FEATURES = (
    ("load", None),
    ("load", ""),
    ("load", "3.0"),
    )

class WidgetDOMImplementation(DOMProxy.DOMImplementationProxy):
    """A proxy of a DOMImplementation node that defines createDocument
    to return a WidgetDocument.
    """

    def hasFeature(self, feature, version):
        feature = string.lower(feature)
        if (feature, version) in _WIDGET_DOM_FEATURES:
            return 1
        if (feature, version) in _WIDGET_DOM_NON_FEATURES:
            return 0
        return DOMProxy.DOMImplementationProxy.hasFeature(self, feature,
                                                          version)

    def createDocumentType(self, qualifiedName, publicId, systemId):
        DOMDocumentType = self._createDOMDocumentType(qualifiedName,
                                                      publicId, systemId)
        return WidgetDocumentType(DOMDocumentType)
    
    def createDocument(self, namespaceURI, qualifiedName, docType=None):
        if docType is not None:
            if docType.ownerDocument is not None:
                raise xml.dom.WrongDocumentErr
            mdocType = docType.getDOMObj()
        else:
            mdocType = None
        DOMDocument = self._createDOMDocument(namespaceURI, qualifiedName,
                                              mdocType)
        return WidgetDocument(DOMDocument)

theDOMImplementation = WidgetDOMImplementation()
    
class WidgetNode(WidgetWrapper, DOMProxy.NodeProxy, WidgetTraversable,
                 Acquisition.Implicit):
    "A wrapper around a DOM Node."
    
class WidgetNodeList(WidgetWrapper, DOMProxy.NodeListProxy,
                     Acquisition.Implicit):
    "A wrapper around a DOM NodeList."
    meta_type = "Widget NodeList"
        
    # redefine to get back the [] syntax with acquisition, eh?
    def __getslice__(self, i, j):
        return self.wrapNodeList(self._node.__getslice__(i,j))

    # redefine to get back the [] syntax with acquisition, eh?
    def __getitem__(self, i):
        return self.wrapDOMObj(self._node.__getitem__(i))        

class WidgetNamedNodeMap(WidgetWrapper, DOMProxy.NamedNodeMapProxy,
                         Acquisition.Implicit):
    "A wrapper around a DOM NamedNodeMap."
    meta_type = "Widget NamedNodeMap"
        
    # redefine to get back the [] syntax with acquisition, eh?
    def __getitem__(self, i):
        return self.wrapDOMObj(self._node.__getitem__(i))        
    
class WidgetDocumentFragment(WidgetWrapper, DOMProxy.DocumentFragmentProxy,
                             WidgetNode):
    "A wrapper around a DOM DocumentFragment."
    meta_type = "Widget Document Fragment"
    
class WidgetElement(WidgetWrapper, DOMProxy.ElementProxy,
                    WidgetNode):
    "A wrapper around a DOM Element."
    meta_type = "Widget Element"

class WidgetCharacterData(WidgetWrapper,
                          DOMProxy.CharacterDataProxy, WidgetNode):
    "A wrapper around a DOM CharacterData."
    meta_type = "Widget Character Data"

class WidgetCDATASection(WidgetWrapper,
                         DOMProxy.CDATASectionProxy, WidgetNode):
    "A wrapper around a DOM CDATASection."
    meta_type = "Widget CDATASection"

class WidgetText(WidgetWrapper,
                 DOMProxy.TextProxy, WidgetCharacterData):
    "A wrapper around a DOM Text."
    meta_type = "Widget Text"

class WidgetComment(WidgetWrapper,
                    DOMProxy.CommentProxy, WidgetCharacterData):
    "A wrapper around a DOM Comment."
    meta_type = "Widget Comment"    

class WidgetProcessingInstruction(WidgetWrapper,
                                  DOMProxy.ProcessingInstructionProxy,
                                  WidgetNode):
    "A wrapper around a DOM ProcessingInstruction."
    meta_type = "Widget Processing Instruction"    

class WidgetAttr(WidgetWrapper, DOMProxy.AttrProxy, WidgetNode):
    "A wrapper around a DOM Attr."
    meta_type = "Widget Attr"    

#WidgetDocument is not necessarily a persistent object, even when a
#persistent subclass such as ParsedXML has been instantiated.  Traversing
#up to the document can create a new transient proxy.  Persistent attributes
#must be set on the persistent version.
class WidgetDocument(WidgetWrapper, DOMProxy.DocumentProxy,
                     WidgetNode):
    "A wrapper around a DOM Document."
    meta_type = "Widget Document"    

    implementation = theDOMImplementation

    def __init__(self, node, persistentDocument = None):
        WidgetNode.__init__(self, node, persistentDocument)

    def _get_implementation(self):
        return self.implementation
    
    #block set of implementation, since we don't proxy it the same
    def __setattr__(self, name, value):
        if name == "implementation":
            raise xml.dom.NoModificationAllowedErr()
        WidgetDocument.inheritedAttribute('__setattr__')(self, name, value)

# DOM extended interfaces

class WidgetEntityReference(WidgetWrapper,
                            DOMProxy.EntityReferenceProxy,
                            WidgetNode):
    "A wrapper around a DOM EntityReference."
    meta_type = "Widget Entity Reference"
    
class WidgetEntity(WidgetWrapper, DOMProxy.EntityProxy,
                   WidgetNode):
    "A wrapper around a DOM Entity."
    meta_type = "Widget Entity"

class WidgetNotation(WidgetWrapper, DOMProxy.NotationProxy,
                     WidgetNode):
    "A wrapper around a DOM Notation."
    meta_type = "Widget Notation"
    
class WidgetDocumentType(WidgetWrapper, DOMProxy.DocumentTypeProxy,
                         WidgetNode):
    "A wrapper around a DOM DocumentType."
    meta_type = "Widget Document Type"    


Node = xml.dom.Node
WRAPPER_TYPES = {
    Node.ELEMENT_NODE: WidgetElement,
    Node.ATTRIBUTE_NODE: WidgetAttr,
    Node.TEXT_NODE: WidgetText,
    Node.CDATA_SECTION_NODE: WidgetCDATASection,
    Node.ENTITY_REFERENCE_NODE: WidgetEntityReference,
    Node.ENTITY_NODE: WidgetEntity,
    Node.PROCESSING_INSTRUCTION_NODE: WidgetProcessingInstruction,
    Node.COMMENT_NODE: WidgetComment,
    Node.DOCUMENT_NODE: WidgetDocument,
    Node.DOCUMENT_TYPE_NODE: WidgetDocumentType,
    Node.DOCUMENT_FRAGMENT_NODE: WidgetDocumentFragment,
    Node.NOTATION_NODE: WidgetNotation,
    }
del Node
