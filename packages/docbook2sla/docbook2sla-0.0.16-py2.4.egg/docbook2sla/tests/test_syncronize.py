import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

# Scribus XML Schema
scribus_schema = os.path.join(os.path.dirname(__file__), '..', 'schema', 'scribus.xsd')
xmlschema_doc = etree.parse(scribus_schema)
xmlschema = etree.XMLSchema(xmlschema_doc)

class SyncronizeScribusDocument01TestCase(unittest.TestCase):

    def setUp(self):
        self.d2s = DocBook2Sla()
        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/01_docbook.xml',
                                            'tests/data/test_syncronize/01_scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testValidateOutput(self):
        """ Validate output against XML Schema """
        doc = etree.parse(StringIO(self.output))
        self.failUnless(xmlschema.validate(doc), xmlschema.assertValid(doc))

    def testScribusRoot(self):
        """ Test if the Scribus root node is existent """
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

    def testNumberOfPageobjects(self):
        """ Test the number of pageobjects """
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 6.0)

    def testSimplePageobjects(self):
        """ Test if simple pageobjects are existent """
        first_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id001'])")
        self.assertEqual(first_node, 1.0)

        second_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id002'])")
        self.assertEqual(second_node, 1.0)

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id004'])")
        self.assertEqual(third_node, 1.0)

    def testSimplePageobjectsContent(self):
        """ Test if simple pageobjects contain the correct content """
        content002 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id001']/ITEXT/@CH")
        self.assertEqual(content002, ['Article 1 DocBook Title'])

        content003 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id002']/ITEXT/@CH")
        self.assertEqual(content003, ['Article 1 DocBook Subtitle'])

        content004 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id004']/ITEXT/@CH")
        self.assertEqual(content004, ['\n\t\tArticle 1 DocBook First Blockquote\n\t'])

    def testComplexPageobjects(self):
        """ Test if complex pageobjects are in the output """
        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id003'])")
        self.assertEqual(third_node, 1.0)

    def testComplexPageobjectsContent(self):
        """ Test if complex pageobjects contain the correct content """
        content001 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id003']/ITEXT/@CH")
        self.assertEqual(content001, ['Article 1 DocBook First Para.', 'Article 1 DocBook First Subheadline', 'Article 1 DocBook Second Para', 'Article 1 DocBook Third Para', 'Article 1 DocBook Fourth Para', 'Article 1 DocBook Second Subheadline', 'Article 1 DocBook Sixt Para', 'Article 1 DocBook Seventh Para'])

    def testAdditionalDocBookContent(self):
        additional = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id005'])")
        self.assertEqual(additional, 1.0)

    def testMetadataSource(self):
        pass

class SyncronizeScribusDocument02TestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/02_docbook.xml',
                                            'tests/data/test_syncronize/02_scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

#    def testValidateOutput(self):
#        """ Validate output against XML Schema """
#        doc = etree.parse(StringIO(self.output))
#        valid = xmlschema.validate(doc)
#        self.assertEqual(valid, True, xmlschema.assertValid(doc))

    def testSyncronizeArticle(self):
        """ Test syncronize() function with DocBook article """

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

        # make sure all pageobjects are available
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)

    def testSimplePageobjects(self):
        """ Test if simple pageobjects are in the output """

        first_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id001'])")
        self.assertEqual(first_node, 1.0)

        second_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id002'])")
        self.assertEqual(second_node, 1.0)

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id004'])")
        self.assertEqual(third_node, 1.0)

    def testSimplePageobjectsContent(self):
        """ Test if simple pageobjects contain the correct content """
        # TODO !!!
        #content001 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id001']/ITEXT/@CH")
        #self.assertEqual(content001, ['Article 1 DocBook Title'])

        content002 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id002']/ITEXT/@CH")
        self.assertEqual(content002, ['Article 1 DocBook Subtitle'])

        content004 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id004']/ITEXT/@CH")
        self.assertEqual(content004, ['Article 1 DocBook First Blockquote'])


    def testComplexPageobjects(self):
        """ Test if complex pageobjects are in the output """

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id003'])")
        self.assertEqual(third_node, 1.0)

    def testComplexPageobjectsContent(self):
        """ Test if complex pageobjects contain the correct content """

        content003 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id003']/ITEXT/@CH")
        self.assertEqual(content003, ['Article 1 DocBook First Para.', 'Article 1 DocBook First Subheadline', 'Article 1 DocBook Second Para', 'Article 1 DocBook Third Para', 'Article 1 DocBook Fourth Para', 'Article 1 DocBook Second Subheadline', 'Article 1 DocBook Sixt Para', 'Article 1 DocBook Seventh Para'])


class SyncronizeScribusDocument03TestCase(unittest.TestCase):
    """ An existing Scribus document, with page objects that have no corresponding
        DocBook node, is syncronized with a new DocBook document with additional elements.
    """

    def setUp(self):

        self.d2s = DocBook2Sla()
        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/03_docbook.xml',
                                            'tests/data/test_syncronize/03_scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testValidateOutput(self):
        """ Validate output against XML Schema """
        doc = etree.parse(StringIO(self.output))
        self.failUnless(xmlschema.validate(doc), xmlschema.assertValid(doc))

    def testScribusRoot(self):
        """ Test if the Scribus root node is existent """
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

    def testNumberOfPageobjects(self):
        """ Test the number of pageobjects (4 from DocBook, 29 from Scribus) """
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 33.0)

    def testCreatedSimplePageobjects(self):
        """ Test if newly created simple pageobjects are existent """
        first_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id001'])")
        self.assertEqual(first_node, 1.0)

        second_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id002'])")
        self.assertEqual(second_node, 1.0)

        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id004'])")
        self.assertEqual(third_node, 1.0)

    def testCreatedSimplePageobjectContent(self):
        """ Test if newly created simple pageobject contain the correct content """
        content002 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id001']/ITEXT/@CH")
        self.assertEqual(content002, ['Article 1 DocBook Title'])

        content003 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id002']/ITEXT/@CH")
        self.assertEqual(content003, ['Article 1 DocBook Subtitle'])

        content004 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id004']/ITEXT/@CH")
        self.assertEqual(content004, ['Article 1 DocBook First Blockquote'])

    def testCreatedComplexPageobjects(self):
        """ Test if newly created complex pageobjects are in the output """
        third_node = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='id003'])")
        self.assertEqual(third_node, 1.0)

    def testCreatedComplexPageobjectsContent(self):
        """ Test if newly created complex pageobjects contain the correct content """
        content003 = self.outputtree.xpath("//PAGEOBJECT[@ANNAME='id003']/ITEXT/@CH")
        self.assertEqual(content003, ['Article 1 DocBook First Para.', 'Article 1 DocBook First Subheadline', 'Article 1 DocBook Second Para', 'Article 1 DocBook Third Para', 'Article 1 DocBook Fourth Para', 'Article 1 DocBook Second Subheadline', 'Article 1 DocBook Sixt Para', 'Article 1 DocBook Seventh Para'])

class RejectInvalidInputTestCase(unittest.TestCase):

    def setUp(self):

        # instance
        self.d2s = DocBook2Sla()

class SyncronizeWithAdditionalScribusPageobjectsTestCase(unittest.TestCase):

    def setUp(self):

        # instance
        self.d2s = DocBook2Sla()

        self.outputfn = self.d2s.syncronize('tests/data/test_syncronize/01_docbook.xml',
                                            'tests/data/test_syncronize/01_scribus.sla')
        self.output = open(self.outputfn, 'r').read()
        self.outputtree = etree.XML(self.output)

    def testValidateOutput(self):
        """ Validate output against XML Schema """
        doc = etree.parse(StringIO(self.output))
        valid = xmlschema.validate(doc)
        self.assertEqual(valid, True, xmlschema.assertValid(doc))

    def testOutputIsScribus(self):

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = self.outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

    def testPageobjects(self):
        """ Test if all pageobjects are in the output file """

        # make sure all pageobjects are available
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 6.0)

    def testAdditionalPageobjectIsValid(self):
        """ Test if additional pageobjects in Scribus are preserved """

        # make sure all pageobjects are available
        additional_pageobject = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='IGNORE_ME'])")
        self.assertEqual(additional_pageobject, 1.0)

def test_suite():

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeScribusDocument01TestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeScribusDocument02TestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    #suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeScribusDocument03TestCase)
    #unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(RejectInvalidInputTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeWithAdditionalScribusPageobjectsTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return suite

if __name__ == "__main__":
    test_suite()