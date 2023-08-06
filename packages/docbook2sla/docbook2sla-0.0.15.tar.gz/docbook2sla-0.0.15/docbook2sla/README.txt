================================================
A Python interface to convert DocBook to Scribus
================================================

The docbook2sla package helps you to convert DocBook XML into the Scribus
(http://www.scribus.net) file format.


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

- https://svn.zmag.de/svn/python/docbook2sla/trunk/

Known Issues
============

- currently only a very limited subset of the DocBook syntax is supported: book, part, section, title, subtitle, author, para, bridgehead and blockquote.

Usage
=====

Example from the Python command-line::

  from docbook2sla import DocBook2Sla
  d2s = DocBook2Sla()
  print d2s.create('tests/data/xml/content.xml',
                   'tests/data/scribus/clean134.sla',
                   output_filename='tests/data/output/create_output.sla')
  print d2s.syncronize('tests/data/xml/content-1.xml',
                       'tests/data/output/create_output.sla',
                       'tests/data/output/syncronize_output.sla')

License
=======

GPL


Author
======

Timo Stollenwerk | timo@zmag.de