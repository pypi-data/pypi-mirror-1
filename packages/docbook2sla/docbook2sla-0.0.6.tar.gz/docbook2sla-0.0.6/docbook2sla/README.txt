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

- https://svn.zmag.de/svn/python/docbook2sla/trunk/


Usage
=====

Example from the Python command-line::

  from docbook2sla import DocBook2Sla
  d2s = DocBook2Sla()
  print d2s.create('tests/data/xml/content.xml',\
                   'tests/data/scribus/clean134.sla',\
                   output_filename='tests/data/output/create_output.sla')
  print d2s.syncronize('tests/data/xml/content-1.xml',\
                       'tests/data/output/create_output.sla',\
                       'tests/data/output/syncronize_output.sla')



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