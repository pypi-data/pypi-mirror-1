humboldt.cmfbibliographyat
==========================

.. contents::

Requirements
------------

* Products.CMFBibliography 1.0.0 or higher



SFX server integration
----------------------

The module provides a propertysheet ``portal_properties`` ->
``cmfbibliographyat`` where you can enable the SFX server integration support
(``SFX integration`` property). The ``Metaresolver URL`` property allows you to
specify a meta-resolver (e.g. http://www.worldcat.org)


Syndication support
-------------------
``humboldt.cmfbibliographyat`` supports syndication out-of-the-box. 

Prequisites:
++++++++++++

- enable the ``syndication`` action in ``portal_actions`` -> ``object`` -> ``syndication`` by
  toggling the ``Visible`` checkbox
- visit the ``Syndication`` tab of your bibliographic folder and enable syndication

Using syndication support
+++++++++++++++++++++++++

- add ``@@atom.xml`` or ``@@rss.xml`` to the URL of your bibliographic folder

- there is also a document action ``ATOM Feed`` pointing the ``@@atom.xml`` URL

- an optional request parameter ``detail_view`` can be set to 
  ``simple_entry_view`` or ``full_entry_view`` (default) providing additional 
  information for each bibliographic item referenced within the feed::

    http://example.org/plone/bib_folder/@@atom.xml?detail_view=simple_entry_view

Credits
-------
``humboldt.cmfbibliographyat`` is funded by the Humboldt University of Berlin

License
-------
``humboldt.cmfbibliographyat`` is published under the GNU Publice License V2 (GPL) 

Author
------

| Andreas Jung
| ZOPYX Ltd. & Co. KG
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-Mail: info@zopyx.com
| Web: http://www.zopyx.com


