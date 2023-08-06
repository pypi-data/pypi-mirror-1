#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Timo Stollenwerk (timo@zmag.de)"
__license__ = "GNU General Public License (GPL)"
__revision__ = "$Rev: 178 $"
__date__ = "$Date: 2008-03-01 23:21:48 +0100 (Sat, 01 Mar 2008) $"
__URL__ = "$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/interfaces.py $"

from zope.interface import Interface

class IDocBook2Sla(Interface):

    def convert(docbook_filename, scribus_filename):
        """ Merge a DocBook and a Scribus file (stored on the filesystem) to some output format.
            Returns the filename of the output file.
        """
