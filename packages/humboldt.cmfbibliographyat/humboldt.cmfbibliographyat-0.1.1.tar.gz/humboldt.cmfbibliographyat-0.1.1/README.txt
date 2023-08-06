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
``humboldt.cmfbibliographyat`` support syndication out-of-the-box. 

Prequisites:
++++++++++++

- enable the ``syndication`` action in ``portal_actions`` -> ``object`` -> ``syndication`` by
  toggling the ``Visible`` checkbox
- visit the ``Syndication`` tab of your bibliographic folder and enable syndication

Using syndication support
+++++++++++++++++++++++++

- add ``@@atom.xml`` or ``@@rss.xml`` to the URL of your bibliographic folder

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


