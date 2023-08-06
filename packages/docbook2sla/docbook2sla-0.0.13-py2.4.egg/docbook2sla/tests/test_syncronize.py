import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class SyncronizeScribusDocumentTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/docbook.xml',
                                            'tests/data/test_syncronize/scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testSyncronizeArticle(self):
        """ Test syncronize() function with DocBook article """

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

        # make sure all pageobjects are available
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 5.0)

    def testSimplePageobjects(self):
        """ Test if simple pageobjects are in the output """

        first_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id002'])")
        self.assertEqual(first_node, 1.0)

        second_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id003'])")
        self.assertEqual(second_node, 1.0)

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id004'])")
        self.assertEqual(third_node, 1.0)

    def testComplexPageobjects(self):

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id001'])")
        self.assertEqual(third_node, 1.0)

class RejectInvalidInputTestCase(unittest.TestCase):

    def setUp(self):

        # instance
        self.d2s = DocBook2Sla()

class SyncronizeWithAdditionalScribusPageobjectsTestCase(unittest.TestCase):

    def setUp(self):

        # instance
        self.d2s = DocBook2Sla()

        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/docbook.xml',
                                            'tests/data/test_syncronize/scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testOutputIsScribus(self):

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

    def testPageobjects(self):
        """ Test if all pageobjects are in the output file """

        # make sure all pageobjects are available
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 5.0)

    def testAdditionalPageobjectIsValid(self):
        """ Test if additional pageobjects in Scribus are preserved """

        # make sure all pageobjects are available
        additional_pageobject = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='IGNORE_ME'])")
        self.assertEqual(additional_pageobject, 1.0)

def test_suite():

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeScribusDocumentTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(RejectInvalidInputTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeWithAdditionalScribusPageobjectsTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return suite

if __name__ == "__main__":
    test_suite()