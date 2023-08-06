humboldt.cmfbibliographyat
==========================

.. contents::

Requirements
------------

* Products.CMFBibliography 1.0.0 or higher
* optional: Products.ATBiblioStyles


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

- an optional request parameter ``style`` can be set to 
  ``simple``, ``full``:::

        http://example.org/plone/bib_folder/@@atom.xml?style=full

  In addition we support rendering of bibliographic references in different
  styles through the (optionally installed) add-on ATBiblioStyles. Feed entries
  can be styled by specifying the **internal** style name like 
  
    * stl_default
    * stl_minimal
    * stl_chicago
    * stl_harvard
    * stl_mla
    * stl_apa
    * stl_ecosciences

  Example::
  
        http://example.org/plone/bib_folder/@@atom.xml?style=stl_apa

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


