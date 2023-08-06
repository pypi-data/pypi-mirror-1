
XMLWidgets
==========

XMLWidgets can be used to create through the web viewers and editors
of XML content, stored in ParsedXML.

Note: I don't expect people to understand XMLWidgets without far more
information. For now, perhaps an example would help. Silva's editor is
such an example, so you could install Silva and play with it (see
especially the ``service_widgets`` directory, and note the scripts in
``service_setup`` to register any new widgets).

The *XMLWidgets Editor Service* is added just once to a Zope system
and should be called ``service_editor``. It is a singleton which
provides a number of facilities for viewers and editors.

The *XMLWidgets Registry* is used to register widgets (usually simple
Zope folders with content such as page templates and python
scripts). Currently they don't become equipped with any user
interface, so you must use Python Scripts to configure them. The
*XMLWidgets Editor Service* then can use this information to render
documents (possibly in editor mode).
