``Produce & Publish for Plone`` - high-quality export of Plone content to PDF, RTF, ODT, WML and DOCX
=====================================================================================================


``Produce & Publish for Plone`` provides high-quality export to the most common
office formats like PDF, RTF, ODT, DOCX and WML based on XSL-FO. 


Features:
---------

``Produce & Publish for Plone`` can convert the 'content' view of Plone
documents into different formats:

- PDF

- ODT (native Openoffice format)

- RTF (Rich Text Format)

- DOCS (native Microsoft Office 2007 format)

- WML (older Microsoft Office 2003(?) XML-based format)



Other features:
---------------

- customizable templates per content-type

- customizable stylesheets per content-type

- configurable per-content-type content aggregation

- customizable conversion workflow chain e.g. to prepare the HTML
  e.g by removing links or  generating link lists 

- document-structure-driven conversion: e.g. the H1 tags can be used to
  enforce page-breaks in order to use sections starting with a H1 tag as marker
  for a new chapter.


Requirements:
-------------

- zopyx.convert V 1.0.0 or higher, see http://cheeseshop.python.org/pypi/zopyx.convert

- BeautifulSoup

- Plone 3.0, 3.1 (no support for Plone 2.5)

- Javascript-enabled browser

- PIL (Python Imaging Library)


Installation:
-------------

- ensure that **zopyx.convert** is installed **including all its dependencies**

- unpack the ``Products.SmartPrintNG`` archive inside the *Products* folder of your instance home

- add ``Products.SmartPrintNG`` through the **Add/Remove programms** functionalty inside the 
  Plone UI 

- if you create a new Plone site, ensure to pick up the proper extension profile
  matching your Plone version


Using ``Produce & Publish for Plone``:
--------------------------------------

- on Plone 3.0 you will see **Export** as new document action. Clicking on it will
  open the ``Produce & Publish for Plone`` control panel at the bottom of your current page.


License
-------

``Produce & Publish for Plone`` is published under LGNU Public License V 3.0 (LGPL 3.0). 


Copyright
---------

``Produce & Publish for Plone`` is (C) 2007, 2008, ZOPYX Ltd. & Co KG, Charlottenstr. 37/1,
D-72070 Tuebingen, Germany


Author
------

``Produce & Publish for Plone`` was written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen,
Germany.


Contact
-------

| ZOPYX Ltd & Co. KG
| c/o Andreas Jung
| Charottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com or http://www.zopyx.de
