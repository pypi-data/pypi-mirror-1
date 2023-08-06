import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class CreateScribusDocumentTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

    def testCreateArticle(self):
        """ Test create() function with DocBook article """

        outputfn = self.d2s.create('tests/data/xml/article+id.xml',
                                   'tests/data/scribus/clean134.sla')
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)


    def testCreateBook(self):
        """ Test create() function with DocBook book """

        outputfn = self.d2s.create('tests/data/xml/book+id.xml',
                                   'tests/data/scribus/clean134.sla')
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 10.0)

def test_suite():

    suite = unittest.TestLoader().loadTestsFromTestCase(CreateScribusDocumentTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return suite

if __name__ == "__main__":
    test_suite()


