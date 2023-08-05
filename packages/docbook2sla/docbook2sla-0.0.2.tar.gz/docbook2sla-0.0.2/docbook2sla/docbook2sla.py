import os

from util import newTempfile, runcmd
from logger import LOG

from lxml import etree

from zope.interface import implements
from interfaces import IDocBook2Sla

_debug = 0

class NotValidXmlError(Exception): pass

class DocBook2Sla(object):
    """Conversions from DocBook to Scribus
    """

    implements(IDocBook2Sla)

    def __init__(self, docbookfn, scribusfn):
        self.docbookfn = docbookfn
        self.scribusfn = scribusfn

    def convert(self, docbookfn, scribusfn, output_filename=None):
        """ Converts a docbook and a scribus file
        """
        if not output_filename:
            output_filename = newTempfile(suffix='.sla')

        # create instance of DocBook2Sla
        #d2s = DocBook2Sla(docbookfn, scribusfn)

        # validate input files
        #print 'validate docbook: %s' % d2s.validate(docbookfn)
        #print 'validate scribus: %s' % d2s.validate(scribusfn)

        # add id to every docbook node
        docbookfn_with_ids = self.generateId(docbookfn)
        if _debug:
            print 'docbookfn_with_ids: %s' % docbookfn_with_ids

        # transform docbook into scribus pageobjects
        pageobjectsfn = self.docbook2Pageobjects(docbookfn_with_ids)
        if _debug:
            print 'pageobjectsfn: %s' % pageobjectsfn


        # it is necessary to write the content to a named tmpfile, because
        # the wrapper xslt stylesheet needs a static param input
        self.write(pageobjectsfn, 'content.sla')

        # inject the scribus pageobjects into a scribus wrapper file
        scribusfn = self.wrapper(pageobjectsfn)
        if _debug:
            print 'scribusfn: %s' % scribusfn
        print self.showFile(scribusfn)

        self.write(scribusfn, 'output/output.sla')
        if _debug:
            print 'validate %s: %s' % ('output/output.sla', self.validate(scribusfn))

        print self.analyseScribusFile(scribusfn)

        return output_filename

    def validate(self, fname):
        """ validates a xml against its xml schema
        """

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
        """ generates ids for every node of a docbook document
        """

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
        """ Converts docbook nodes into scribus pageobjects
        """

        # file -> elementtree
        docbook = etree.parse(docbookfn)

        # parse the xslt stylesheet
        style = etree.parse('xsl/docbook2pageobject.xsl')

        # load the xslt stylesheet
        xslt = etree.XSLT(style)

        # transform the xml file with the xslt stylesheet
        result = xslt(docbook, uselayout="'../scribus/clean134.sla'")

        filename = newTempfile(suffix='.xml')
        open(filename, 'wb').write(etree.tostring(result.getroot()))
        return filename


    def wrapper(self, contentfn):
        """ Wraps up Scibus pageobjects into a Scribus document
        """

        foo = "bar"
        # parse the scribus wrapper
        scribusfn = 'scribus/clean134.sla'
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
        """ write tempfile into output file
        """
        tmpFile = open(tmpfn,"r")
        outputFile = open(outputfn,"w")
        outputFile.write(tmpFile.read())
        return outputFile.close()

    def analyseScribusFile(self, scribusfn):
        """ returns statistical informations about a scribus file
        """

        # file -> elementtree
        tree = etree.parse(scribusfn)
        return '# Pageobjects: %s' % len(tree.findall(".//PAGEOBJECT"))

    def analyseDocBookFile(self, docbookfn):
        """ returns statistival informations about a docbook file
        """
        pass

    def showFile(self, fn):
        tmpFile = open(fn,"r")
        return tmpFile.read()

    def __call__(self, *args, **kw):
        return self.convert(*args, **kw)