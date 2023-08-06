# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.39 $
import Globals
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from BTrees.OOBTree import OOBTree
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from helpers import add_and_edit
from Persistence import Persistent

CACHE_SIZE = 1000 # max 1000 documents in cache, if more, shrink
CACHE_SHRINK_FACTOR = 2 # shrink cache by which factor if over size

theEditorCache = None

class EditorServiceError(Exception):
    pass

class EditorCache:
    """Rendered widgets cache for EditorService
    """

    def __init__(self,
                 cache_size=CACHE_SIZE,
                 cache_shrink_factor=CACHE_SHRINK_FACTOR):
        self._cache_size = cache_size
        self._cache_shrink_factor = cache_shrink_factor
        self._cache = self._new_mapping()
        
    # MANIPULATORS

    def _new_mapping(self):
        return {}

    def cache(self, document_key, node_path, widget_path, data):
        # compact cache if necessary
        self.compact()
        # now add this to cache
        if not self._cache.has_key(document_key):
            self._cache[document_key] = self._new_mapping()
        self._cache[document_key][(node_path, widget_path)] = data
    
    def invalidate(self, document_key, node_path, widget_path):
        try:
            del self._cache[document_key][(node_path, widget_path)]
        except KeyError:
            pass
        
    def clearDocument(self, document_key):
        try:
            del self._cache[document_key]
        except KeyError:
            pass

    def clear(self):
        self._cache = self._new_mapping()

    def compact(self):
        """Shrink cache is necessary.

        Note that cache shrinking is currently arbitrary, but most used
        documents will appear in the cache again soon enough at only a
        minor penalty of performance, so the simplicity is worth it
        """
        if len(self._cache) < self._cache_size:
            return

        shrinked_size = int(self._cache_size / self._cache_shrink_factor)        
        for i in range(len(self._cache) - shrinked_size):
            # pop items from dict until dict length equals shrinked_size
            self._cache.popitem()

    def setCacheSize(self, size):
        self._cache_size = size

    # ACCESSORS

    def getCached(self, document_key, node_path, widget_path):
        try:
            return self._cache[document_key][(node_path, widget_path)]
        except KeyError:
            return None

class PersistentEditorCache(Persistent, EditorCache):
    """Rendered widgets cache for EditorService

    This cache can be attached to e.g. a Zope folder. This Folder could then 
    be a mount point on a ZEO Storage Server, effectively sharing this cache
    over the ZEO Cluster.
    """

    def _new_mapping(self):
        return OOBTree()

    def compact(self):
        if len(self._cache) < self._cache_size:
            return

        shrinked_size = int(self._cache_size / self._cache_shrink_factor)        
        for i in range(len(self._cache) - shrinked_size):
            # delete items from btree until btree length equals shrinked_size
            key = self._cache.minKey()
            del self._cache[key]

class EditorSession(Persistent):
    def __init__(self):
        self.document_context = {
            'depth': 0,
            'wr_name': None,
            'node_path': None,
            'widget_path': None,
            }
        self.contexts = {}
        self.roots = []

    # MANIPULATORS
    def setDocumentContext(self, wr_name):
        self.document_context['wr_name'] = wr_name
        self.document_context = self.document_context
        
    def setContext(self, node, wr_name):
        self.clearNodeWidget(node)
        self.contexts[node.getNodePath('widget')] = {
            'depth': self.getContext(node)['depth'] + 1,
            'wr_name': wr_name,
            'node_path': None,
            'widget_path': None
            }
        self.contexts = self.contexts
        
    def setNodeWidget(self, node, widget_path):
        self.clearNodeWidget(node)
        context = self.getContext(node)
        context['node_path'] = node.getNodePath('widget')
        context['widget_path'] = widget_path
        self.document_context = self.document_context
        self.contexts = self.contexts
        
    def clearNodeWidget(self, node):
        context = self.getContext(node)
        context['node_path'] = None
        context['widget_path'] = None
        d = context['depth']
        for node_path, context in self.contexts.items():
            if context['depth'] > d:
                del self.contexts[node_path]
        self.contexts = self.contexts
                
    def clearContext(self, node):
        while node is not None:
            node_path = node.getNodePath('widget')
            context = self.contexts.get(node_path)
            if context is not None:
                del self.contexts[node_path]
                self.contexts = self.contexts
                return
            node = node.parentNode
    
    def pushRoot(self, node, wr_name):
        self.setContext(node, wr_name)
        self.roots.append(node.getNodePath('widget'))
        self.roots = self.roots

    def popRoot(self, node):
        self.clearContext(node)
        self.roots.pop()
        self.roots = self.roots
        
    # ACCESSORS
    def getContext(self, node):
        if not self.contexts:
            return self.document_context
        while node is not None:
            context = self.contexts.get(node.getNodePath('widget'))
            if context is not None:
                return context
            node = node.parentNode
        return self.document_context

    def getRoot(self):
        if self.roots:
            return self.roots[-1]
        else:
            return None
        
class EditorService(SimpleItem):
    """A user using an editor uses the editor session (which uses
    Zope's sessions).
    """

    security = ClassSecurityInfo()
    
    meta_type = "XMLWidgets Editor Service"

    cache_container_id = None

    cache_size = CACHE_SIZE
    cache_shrink_factor = CACHE_SHRINK_FACTOR
    
    manage_options = (
        {'label':'Info', 'action':'info_tab'},
        {'label':'Edit', 'action':'manage_editorServiceCacheEditTab'},
        ) + SimpleItem.manage_options

    security.declareProtected(
        'View management screens', 'manage_editorServiceCacheEditTab')
    manage_editorServiceCacheEditTab = PageTemplateFile(
        'www/editorServiceEditTab', globals(), 
        __name__='manage_editorServiceCacheEditTab')

    security.declareProtected(
        'View management screens', 'info_tab')
    manage_main = info_tab = PageTemplateFile(
        'www/editorServiceInfoTab', globals(),  __name__='info_tab')

    def __init__(self, id, title):
        self.id = id
        self.title = title

    # MANIPULATORS
    security.declareProtected(
        'View management screens', 'manage_editorServiceCacheEditTab')
    def manage_editorServiceCacheEdit(self, id, size):
        """set the cache container
        """
        msg = 'Settings changed.'

        if not id:
            # id left empty, use None - use in-memory cache
            id = None
            msg += ' Id left empty, so using in-memory cache.'        
        elif getattr(self.aq_inner, id, None) is None:
            # not a valid object, report that..
            return self.manage_editorServiceCacheEditTab(
                manage_tabs_message='Id does not provide for an existing cache container.')

        # Set parameters.
        self.cache_container_id = id
        self.cache_size = size  
        # Set it on the live cache object too, and compact it.
        cache = self._get_editor_cache()
        cache.setCacheSize(size)
        cache.compact()

        return self.manage_editorServiceCacheEditTab(manage_tabs_message=msg)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'setDocumentEditor')
    def setDocumentEditor(self, node, wr_name):
        self._createEditorSession(node)
        self._getEditorSession(node).setDocumentContext(wr_name)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'setEditor')    
    def setEditor(self, node, wr_name):
        self._getEditorSession(node).setContext(node, wr_name)

    security.declareProtected('View',
                              'setViewer')
    def setViewer(self, wr_name):
        self.REQUEST.set('xmlwidgets_viewer', wr_name)
        
    security.declareProtected('Use XMLWidgets Editor Service',
                              'clearEditor')
    def clearEditor(self, node):
        self._getEditorSession(node).clearContext(node)
        
    security.declareProtected('Use XMLWidgets Editor Service',
                              'setNodeWidget')
    def setNodeWidget(self, node, widget_path):
        self._getEditorSession(node).setNodeWidget(node, widget_path)
        
    security.declareProtected('Use XMLWidgets Editor Service',
                              'clearNodeWidget') 
    def clearNodeWidget(self, node):
        self._getEditorSession(node).clearNodeWidget(node)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'pushRoot')
    def pushRoot(self, node, wr_name):
        self._getEditorSession(node).pushRoot(node, wr_name)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'popRoot')
    def popRoot(self, node):
        self._getEditorSession(node).popRoot(node)

    # ACCESSORS

    security.declareProtected('Use XMLWidgets Editor Service',
                              'getRoot')
    def getRoot(self, node):
        document = node.ownerDocument
        editor_session = self._getEditorSession(node)
        if editor_session is None:
            return document.documentElement
        root = editor_session.getRoot()
        if root is not None:
            return document.resolveNodePath(root)
        else:
            return document.documentElement

    security.declareProtected('View', 'getViewer')
    def getViewer(self):
        return getattr(self, self.REQUEST['xmlwidgets_viewer'])

    security.declareProtected('Use XMLWidgets Editor Service',
                              'getNode')
    def getNode(self, node):
        """Get the highlighted node in context.
        """
        node_path = self._getEditorSession(node).getContext(None)['node_path']
        if node_path is not None:
            to_ret = node.ownerDocument.resolveNodePath(node_path)
            return to_ret
        else:
            return None
        
    security.declareProtected('View', 'renderView')
    def renderView(self, node):
        # NOTE: Need to store viewer as it may change otherwise
        # during rendering XXX does this still make sense?
        viewer = self.getViewer()
        return viewer.getWidget(node).render()

    security.declareProtected('View', 'renderElementsView')
    def renderElementsView(self, node):
        # NOTE: Need to store viewer as it may change otherwise
        # during rendering XXX does this still make sense?
        viewer = self.getViewer()
        return ''.join([viewer.getWidget(child).render()
                        for child in node.childNodes
                        if child.nodeType == node.ELEMENT_NODE])

    security.declareProtected('Use XMLWidgets Editor Service',
                              'render')
    def render(self, node):
        document_key = self._getDocumentKey(node)
        node_path = node.getNodePath('widget')
        context = self._getEditorSession(node).getContext(node)
        widget_path = self._getWidgetPathInContext(context, node)
        request = self.REQUEST
        request['node'] = node
        request.wr_name = context['wr_name']
        cache = self._get_editor_cache()
        data = cache.getCached(document_key, node_path, widget_path)
        if data is None:
            widget = self._resolveWidgetPath(widget_path)
            __traceback_info__ = ('/'.join(widget_path), widget)
            data = widget.render()
            if getattr(widget, 'cached', lambda: 0)():
#                print "Caching:", widget_path, node_path
                cache.cache(
                    document_key, node_path, widget_path, data)
#            else:
#                print "Not caching:", widget_path, node_path
#        else:
#            print "Retrieving:", widget_path, node_path
        return data

    # XXX renderCache deprecated
    security.declareProtected('Use XMLWidgets Editor Service',
                              'renderCache')
    renderCache = render
    
    security.declareProtected('Use XMLWidgets Editor Service',
                              'renderElements')
    def renderElements(self, node):
        return ''.join([self.render(child)
                        for child in node.childNodes if
                        child.nodeType == node.ELEMENT_NODE])

    # XXX renderElementsCache deprecated
    security.declareProtected('Use XMLWidgets Editor Service',
                              'renderElementsCache')
    renderElementsCache = renderElements
    
    security.declareProtected('Use XMLWidgets Editor Service',
                              'invalidateWidgetCache')
    def invalidateWidgetCache(self, node, widget_path):
        """Invalidates cache for 'modeless' widgets"""
        document_key = self._getDocumentKey(node)
        cache = self._get_editor_cache()
        cache.invalidate(
            document_key,
            node.getNodePath('widget'),
            widget_path)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'invalidateWidgetCaches')
    def invalidateWidgetCaches(self, node, widget_path, modes):
        document_key = self._getDocumentKey(node)
        node_path = node.getNodePath('widget')
        editor_session = self._getEditorSession(node)
        cache = self._get_editor_cache()
        for mode in modes:            
            cache.invalidate(
                document_key,
                node_path,
                widget_path + (mode,))
        
    security.declareProtected('Use XMLWidgets Editor Service',
                              'invalidateCaches')
    def invalidateCaches(self, node, modes):
        widget_path = self._getWidgetPath(node)[:-1]
        document_key = self._getDocumentKey(node)
        node_path = node.getNodePath('widget')
        editor_session = self._getEditorSession(node)
        cache = self._get_editor_cache()
        for mode in modes:            
            cache.invalidate(
                document_key,
                node_path,
                widget_path + (mode,))
        
    security.declareProtected('Use XMLWidgets Editor Service',
                              'invalidateChildCaches')
    def invalidateChildCaches(self, node, modes):
        """Invalidate cache of children (one level)
        """
        for child in node.childNodes:
            if child.nodeType != node.ELEMENT_NODE:
                continue
            self.invalidateCaches(child, modes)
    
    security.declareProtected('Use XMLWidgets Editor Service',
                              'clearCache')    
    def clearCache(self, node):
        cache = self._get_editor_cache()
        cache.clearDocument(self._getDocumentKey(node))

    security.declareProtected('Use XMLWidgets Editor Service',
                              'getWidget')
    def getWidget(self, node):
        context = self._getEditorSession(node).getContext(node)
        self.REQUEST['node'] = node
        self.REQUEST.wr_name = context['wr_name']
        widget_path = self._getWidgetPathInContext(context, node)
        if widget_path is None:
            raise EditorServiceError, "Unknown widget for node: %s" % node.nodeName
        return self._resolveWidgetPath(widget_path)

    security.declareProtected('Use XMLWidgets Editor Service',
                              'hasNodeWidget')
    def hasNodeWidget(self, node):
        context = self._getEditorSession(node).getContext(node)
        return context['node_path'] is not None
    
    security.declareProtected('Use XMLWidgets Editor Service',
                              'getNodeWidgetPath')
    def getNodeWidgetPath(self, node):
        editor_session = self._getEditorSession(node)
        if not editor_session:
            return None
        return editor_session.getContext(node)['widget_path']
    
    # HELPERS

    def _getWidgetPathInContext(self, context, node):
        if (context['node_path'] and
            node.getNodePath('widget') == context['node_path']):
            return context['widget_path']
        else:
            return getattr(self, context['wr_name']).findWidget(node)
        
    def _getWidgetPath(self, node):
        context = self._getEditorSession(node).getContext(node)
        return self._getWidgetPathInContext(context, node)
        
    def _resolveWidgetPath(self, widget_path):
        obj = self.aq_inner
        for step in widget_path:
            obj = getattr(obj, step, None)
            if obj is None:
                raise AttributeError, \
                      ( 'XML Editor Service %s cannot acquire %s ("%s" not found)' % \
                        ( self.getId(), '/'.join(widget_path), step ) )
        return obj

    def _createEditorSession(self, node):
        session = self.REQUEST.SESSION
        session_data = session.get('xmlwidgets_service_editor', {})
        document_key =  self._getDocumentKey(node)
        if session_data.has_key(document_key):
            return
        editor_session = session_data[document_key] = EditorSession()
        session['xmlwidgets_service_editor'] = session_data
        
    def _getEditorSession(self, node):
        try:
            document_key = self._getDocumentKey(node)
            return self.REQUEST.SESSION[
                'xmlwidgets_service_editor'][document_key]
        except KeyError:
            return None

    def _getDocumentKey(self, node):
        if node.nodeType == node.DOCUMENT_NODE: 	 
            doc = node 	 
        else: 	 
            doc = node.ownerDocument
            
        request = self.REQUEST        
        path =  doc.getPhysicalPath()
        return (request['SERVER_URL'], tuple(request._script), path)        
        
    def _get_editor_cache(self):
        if self.cache_container_id is None:
            # Do not attach cache to a container - use in-memory cache
            # using theEditorCache singleton.
            global theEditorCache
            if theEditorCache is None:
                theEditorCache = EditorCache(
                    cache_size=self.cache_size,
                    cache_shrink_factor=self.cache_shrink_factor)                
            return theEditorCache
        else:
            # Attach cache to a container - useful for sharing the cache
            # over ZEO clients (this container should then be mounted
            # from the ZEO Storage Server).
            cc = getattr(self.aq_inner, self.cache_container_id)
            storage = getattr(cc, 'widget_editor_cache', None)
            if storage is None:
                cc.widget_editor_cache = PersistentEditorCache(
                    cache_size=self.cache_size,
                    cache_shrink_factor=self.cache_shrink_factor)
                # Trigger persistence machinery
                cc._p_changed = 1
                storage = cc.widget_editor_cache
            return storage
        
Globals.InitializeClass(EditorService)

manage_addEditorServiceForm = PageTemplateFile(
    "www/editorServiceAdd", globals(),
    __name__='manage_addEditorServiceForm')

def manage_addEditorService(self, id, title="", REQUEST=None):
    """Add Editor service to folder.
    """
    # add actual object
    id = self._setObject(id, EditorService(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
