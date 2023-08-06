Description
===========

The main content types provided are:

  * Normativa, stores a legislative document in binary format and its metadata.

  * Area, a folderish content type where normativas can be added and
    categorized.


Dependencies
============

This product should work with the whole Plone 3 serie. Nevertheless, is was
only tested in Plone 3.3rc2. The following products must be installed in your
site before installing Products.DigestoContentType:

  * Products.ATExtensions 0.9.5

  * iw.fss 2.7.6

  * Products.ATBackRef 2.0

  * Products.CMFPlacefulWorkflow (which already comes with Plone)


Installation
============

Make sure that all the dependencies are installed. If you use zc.buildout, just
add Products.DigestoContentTypes to your eggs and zcml and rerun buildout. In
the site install all the dependencies and finally Products.DigestoContentTypes.

A sample buildout can be found in the product's SVN repository:
http://svn.plone.org/svn/collective/Products.DigestoContentTypes/buildout. That
buildout can be used to quickly try the product or serve as a base to modify
your own buildout configuration.


Development
===========

This product was generated using ArchGenXML.

You can build the development buildout by running the following commands:

$ svn co http://svn.plone.org/svn/collective/Products.DigestoContentTypes/buildout digesto
$ cd digesto
$ python2.4 bootstrap.py
$ ./bin/buildout

Then you can start the Zope instance running:

$ ./bin/instance fg

The ZMI can be accessed in http://localhost:8080/manage, where you can
authenticate using 'admin' as user id and password.


Credits
=======

This product was developed by Emanuel Sartor and Santiago Bruno from Menttes.
The development was sponsored by the Universidad Nacional de Córdoba and
Menttes.


Acknowlegements
===============

The attachment management widget was originally created by Martin Aspeli for
the RichDocument product. The templates can be found in:
skins/digestocontenttypes_templates/widget_attachments*; the widget
class is in the 'widget' directory.

The dynamic sequence widget was created by Philipp von Weitershausen in his
demo application for the "Web Component Development with Zope 3" book. Files:
browser/widget.py, browser/templates/widget.pt and
browser/resources/sequence.js.

The normativas live search is highly based on the Plone live search. Files:
browser/resources/normativalivesearch.js,
skins/digestocontenttypes_templates/normativa_livesearch_reply.py.

The normativas search and 'send to' functionalities is derived from Plone's
search and 'send to' functioanlities. Files (all of them in
skins/digestocontenttypes_templates/): normativa_search.pt, normativa_send.cpt,
normativa_sendto.cpy.

The are a bunch on templates derived from Archetypes templates. Archetypes was
written by Benjamin Saller and others. All the derived files are in the
skins/digestocontenttypes_templates/ directory:

  * The files area_view.pt and normativa_view.pt are derived from the
    base_view.pt template.

  * The file edit_macros_attachments.pt is derived from edit_macros.pt.

  * The file manage_attachments.cpt is derived from base_edit.cpt.

The records widget is derived from the ATExtensions records widget.
ATExtensions was written by Raphael Ritz. File:
skins/digestocontenttypes_templates/dct_records_widget.pt.

The mock mail host utility is derived from the one in PasswordResetTool, by
J. Cameron Cooper. File: tests/utils.py.

This product was generated using ArchGenXML by Phil Auersperg, Jens Klein, et
al.
