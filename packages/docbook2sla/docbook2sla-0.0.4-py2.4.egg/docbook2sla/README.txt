================================================
A Python interface to convert DocBook to Scribus
================================================

The docbook2sla package helps you to convert DocBook XML into the Scribus
file format.


Requirements
============

- `BeautifulSoup`__

__ http://www.crummy.com/software/BeautifulSoup/

- `lxml`__

__ http://codespeak.net/lxml/

Installation
============

- install **docbook2sla** either using easy_install or by downloading the sources from the Python Cheeseshop

Supported platforms
===================

Unix


Subversion repository
=====================

- http://213.133.111.168/svn/repos/python/docbook2sla/trunk/


Usage
=====

Example from the Python command-line::

  from docbook2sla import DocBook2Sla
  d2s = DocBook2Sla('docbook.xml', 'scribus.sla')
  print d2s.convert()


Known issues
============


Author
======

Timo Stollenwerk | timo@zmag.de

License
=======

GPL

Contact
=======

Timo Stollenwerk | timo@zmag.de