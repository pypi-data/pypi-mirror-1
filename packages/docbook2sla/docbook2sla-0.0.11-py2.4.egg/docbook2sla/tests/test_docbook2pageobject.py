import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class DocBook2PageobjectTestCase(unittest.TestCase):
    """ Test the docbook2pageobject stylesheet """

    def setUp(self):

        # create instance
        self.d2s = DocBook2Sla()

        # make stylesheet available
        xsl_docbook2pageobject = os.path.abspath(os.path.join(dirname,
                                                              '..',
                                                              'xsl',
                                                              'docbook2pageobject.xsl'))
        if not os.path.exists(xsl_docbook2pageobject):
            raise IOError('%s does not exist' % xsl_docbook2pageobject)

        # transform
        self.outputfn = self.d2s.transform('tests/data/xml/article+id.xml',
                                      xsl_docbook2pageobject)

        # set output
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testNumberOfPageobjects(self):
        """ Test the correct number of pageobjects """

        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)

    def testComplexPageobject(self):
        """ Test that the complex pageobject has the correct number of ITEXT nodes """

        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id2243972']/ITEXT)")
        self.assertEqual(count_pageobjects, 8.0, self.output)

    def testIsValidPageobject(self):
        """ Validate output against XML Schema """

        # make scribus xml schema available
        xml_schema_scribus = os.path.abspath(os.path.join(dirname, 'schema', 'pageobjects.xsd'))
        if not os.path.exists(xml_schema_scribus):
            raise IOError('%s does not exist' % xml_schema_scribus)

        xmlschema_doc = etree.parse(xml_schema_scribus)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        self.assertEqual(True, xmlschema.validate(self.outputtree), self.output)

def test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DocBook2PageobjectTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    return suite

if __name__ == "__main__":
    test_suite()