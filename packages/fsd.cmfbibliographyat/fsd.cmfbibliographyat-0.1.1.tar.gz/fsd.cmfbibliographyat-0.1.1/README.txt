Introduction
============

A simple integration of CMFBibliographyAT with FacultyStaffDirectory


Installation
============

Add ``fsd.bibliographyat`` to the ``eggs`` option and ``zcml`` slug 
option of your buildout.cfg.

Usage 
=====

A ``BibliographyFolder`` can be added either within the FSDDirectory instance
or individually for every ``FSDPerson`` object. On the person level you can
select a new supplementary view 'Co-author publications' displaying all
publications within the FSD instance where the firstname and fullname matches
against the author list of a publication.

Author
======

``fsd.cmfbibliographyat`` was written by Andreas Jung for ZOPYX Ltd. & Co. KG, 
Tuebingen, Germany.


License
=======

``fsd.cmfbibliographyat`` is published under the Zope Public License (ZPL 2.1).
See LICENSE.txt.


Contact
-------

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com

