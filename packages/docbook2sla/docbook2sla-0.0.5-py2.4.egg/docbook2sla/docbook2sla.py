#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Timo Stollenwerk (timo@zmag.de)"
__license__ = "GNU General Public License (GPL)"
__revision__ = "$Rev: 199 $"
__date__ = "$Date: 2008-03-04 10:42:05 +0100 (Di, 04 Mrz 2008) $"
__URL__ = "$URL: https://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/docbook2sla.py $"

import os, sys

from util import newTempfile, runcmd
from logger import LOG

from lxml import etree

from zope.interface import implements
from interfaces import IDocBook2Sla

_debug = 1

class NotValidXmlError(Exception): pass

class DocBook2Sla(object):
    """Conversions from DocBook to Scribus. """

    implements(IDocBook2Sla)

    def create(self, docbookfn, scribusfn, output_filename=None, validate=False):
        """ Creates a Scribus file from a DocBook source. """

        if _debug:
            print"---- create ----"

        # validate input files
        if validate:
            print 'validate docbook: %s' % self.validate(docbookfn)
            print 'validate scribus: %s' % self.validate(scribusfn)

        # generate id : content.xml -> content.id.xml
        docbook_with_ids = self.transform(docbookfn, 'xsl/generate-id.xsl')

        #return open(docbook_with_ids, 'r').read()

        # docbook2pageobject : 01_content.id.xml -> pageobjects.xml
        scribus_pageobjects = self.transform(docbook_with_ids,
                                             'xsl/docbook2pageobject.xsl')

        #return open(scribus_pageobjects, 'r').read()

        # wrapper : pageobjects.xml + clean134.sla -> output.sla
        output = self.transform(scribusfn,
                                'xsl/wrapper.xsl',
                                secondinputfn=scribus_pageobjects,
                                )

        #return open(output, 'r').read()

        # write to output filename if specified
        if output_filename:
            open(output_filename, 'w').write(open(output, 'r').read())

        return output_filename

    def syncronize(self, docbookfn, scribusfn, output_filename=None, validate=False):
        """ Syncronize changes in a docbook file into a scribus file. """

        if _debug:
            print"---- syncronize ----"

        # validate input files
        if validate:
            try:
                print 'validate docbook: %s' % self.validate(docbookfn)
                print 'validate scribus: %s' % self.validate(scribusfn)
            except:
                print >>sys.stderr, 'Error validating %s and %s' % (docbookfn, scribusfn)
                raise

        # generate id : content.xml -> content.id.xml
        docbook_with_ids = self.transform(docbookfn, 'xsl/generate-id.xsl')

        # docbook2pageobject : 01_content.id.xml -> pageobjects.xml
        scribus_pageobjects = self.transform(docbook_with_ids,
                                             'xsl/docbook2pageobject.xsl')

        # wrapper : pageobjects.xml + clean134.sla -> output.sla
        output = self.transform(scribusfn,
                                'xsl/wrapper.xsl',
                                secondinputfn=scribus_pageobjects,
                                )

        # write to output filename if specified
        if output_filename:
            open(output_filename, 'w').write(open(output, 'r').read())

        return output_filename

    def transform(self, xmlfn, stylefn, secondinputfn=None, outputfn=None, validate=False):
        """ Transforms a XML document with a XSL stylesheet. """

        # if no output filename is specified, create tempfile
        if not outputfn:
            outputfn = newTempfile(suffix='.xml')

        # try to transform inputfn
        try:
            # xml -> elementtree
            xmltree = etree.parse(xmlfn)

            # parse the xslt stylesheet
            styletree = etree.parse(stylefn)

            # load the xslt stylesheet
            xslt = etree.XSLT(styletree)

            if secondinputfn:

                # get the stylesheet path
                pathname = os.path.dirname(stylefn)
                abspath = os.path.abspath(pathname)
                tmpfile = "%s/tmp.xml" % abspath

                # it is necessary to write the content to a named tmpfile, because
                # the wrapper xslt stylesheet needs a static param input
                # ToDo: named tmpfile
                self.write(secondinputfn, tmpfile)

                # transform the xml file with the xslt stylesheet
                result = xslt(xmltree, secondinput="'tmp.xml'")

                # delete content.sla file
                os.remove(tmpfile)
            else:
                result = xslt(xmltree)

            if result != None:
                # write output file
                open(outputfn, 'w').write(etree.tostring(result.getroot()))

        except:
            print >>sys.stderr, 'Error transforming %s (%s) with %s' % (xmlfn, secondinputfn, stylefn)
            raise

        # return the output filename
        return outputfn

    def validate(self, fname):
        """ Validates XML against DocBook or Scribus XML Schema. """

        # split the filename into name and extension
        fe = os.path.splitext( fname )[1]

        # parse the file
        xmltree = etree.parse(fname)

        # docbook or scribus?
        if fe == '.xml':
            # validate docbook
            xmlschema_doc = etree.parse('http://www.docbook.org/xsd/4.5/docbook.xsd')
            xmlschema = etree.XMLSchema(xmlschema_doc)
            if xmlschema.validate(xmltree):
                return True
            else:
                raise NotValidXmlError, "%s is no valid %s file." % (fname, fe)
        elif fe == '.sla':
            # validate scribus
            xmlschema_doc = etree.parse('schema/scribus.xsd')
            xmlschema = etree.XMLSchema(xmlschema_doc)
            if xmlschema.validate(xmltree):
                return True
            else:
                raise NotValidXmlError, "%s is no valid %s file." % (fname, fe)
        else:
            raise ValueError('Unsupported format: %s' % fe)

    def generateId(self, docbookfn):
        """ Generates IDs for every node of a DocBook file. """

        # file -> elementtree
        docbook = etree.parse(docbookfn)

        # parse the xslt stylesheet
        style = etree.parse('xsl/generate-id.xsl')

        # load the xslt stylesheet
        xslt = etree.XSLT(style)

        # transform the xml file with the xslt stylesheet
        result = xslt(docbook)

        filename = newTempfile(suffix='.xml')
        open(filename, 'wb').write(etree.tostring(result.getroot()))
        return filename


    def docbook2Pageobjects(self, docbookfn):
        """ Converts DocBook nodes into Scribus pageobjects. """

        # file -> elementtree
        docbook = etree.parse(docbookfn)

        # parse the xslt stylesheet
        style = etree.parse('xsl/docbook2pageobject.xsl')

        # load the xslt stylesheet
        xslt = etree.XSLT(style)

        # transform the xml file with the xslt stylesheet
        result = xslt(docbook, uselayout="'tests/data/scribus/clean134.sla'")

        filename = newTempfile(suffix='.xml')
        open(filename, 'wb').write(etree.tostring(result.getroot()))
        return filename


    def wrapper(self, contentfn, scribusfn):
        """ Wraps up Scibus pageobjects with a Scribus document. """

        # parse the scribus wrapper
        scribuswrapper = etree.parse(scribusfn)

        # parse the xslt stylesheet
        style = etree.parse('xsl/wrapper.xsl')

        # load the xslt stylesheet
        xslt = etree.XSLT(style)

        # transform the xml file with the xslt stylesheet
        result = xslt(scribuswrapper, content="'../content.sla'")

        filename = newTempfile(suffix='.sla')
        open(filename, 'wb').write(etree.tostring(result.getroot()))
        return filename

    def write(self, tmpfn, outputfn):
        """ Write tempfile into output file. """
        tmpFile = open(tmpfn,"r")
        outputFile = open(outputfn,"w")
        outputFile.write(tmpFile.read())
        return outputFile.close()

    def analyseScribusFile(self, scribusfn):
        """ Returns statistical informations about a Scribus file. """

        # file -> elementtree
        tree = etree.parse(scribusfn)
        return '# Pageobjects: %s' % len(tree.findall(".//PAGEOBJECT"))

    def analyseDocBookFile(self, docbookfn):
        """ Returns statistival informations about a DocBook file. """
        pass

    def showFile(self, fn):
        """ Returns string representation of a file. """
        tmpFile = open(fn,"r")
        return tmpFile.read()

    def __call__(self, *args, **kw):
        return self.create(*args, **kw)