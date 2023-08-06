import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class TransformationTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()


    def testTransformation(self):
        """ Test transformation function. """

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.input.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.expected.xml')

        # try to transform inputfn
        try:
            outputfn = self.d2s.transform(inputfn, transformfn)
        except:
            print >>sys.stderr, 'Error transforming %s with %s' % (inputfn, transformfn)
            raise

        # open output
        output = open(outputfn, 'r')

        # open expected output
        expected = open(expectedfn, 'r')

        self.assertEqual(output.read(), expected.read())

        return outputfn


    def testTransformationWithParam(self):
        """ Test transformation function (with params). """

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.input.xml')
        secondinputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.secondinput.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.expected.xml')

        # try to transform inputfn
        try:
            outputfn = self.d2s.transform(inputfn, transformfn, secondinputfn=secondinputfn)

        except:
            print >>sys.stderr, 'Error transforming %s with %s' % (inputfn, transformfn)
            raise

        # open output
        output = open(outputfn, 'r').read()

        # open expected output
        expected = open(expectedfn, 'r').read()

        self.assertEqual(output, expected)

        return outputfn


class StylesheetsTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

    def testGenerateId(self):
        """ Test transformation from DocBook to DocBook with unique ids. """
        xsl_generateid = os.path.abspath(os.path.join(dirname,
                                                      '..',
                                                      'xsl',
                                                      'generate-id.xsl'))

        outputfn = self.d2s.transform('tests/data/xml/article.xml',
                                      xsl_generateid)

        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        article_id = outputtree.xpath("count(//*[@id])")
        self.assertEqual(article_id, 3.0)

    def testDocBook2PageobjectsArticle(self):
        """ Test transformation from DocBook article to Scribus pageobjects. """

        xsl_docbook2pageobject = os.path.abspath(os.path.join(dirname,
                                                              '..',
                                                              'xsl',
                                                              'docbook2pageobject.xsl'))
        if not os.path.exists(xsl_docbook2pageobject):
            raise IOError('%s does not exist' % xsl_docbook2pageobject)

        outputfn = self.d2s.transform('tests/data/xml/article.xml',
                                 xsl_docbook2pageobject)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        # 4 pageobjects expected (1 complex, 3 simple)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)


    def testDocBook2PageobjectsBook(self):
        """ Test transformation from DocBook book to Scribus pageobjects. """

        xsl_docbook2pageobject = os.path.abspath(os.path.join(dirname,
                                                              '..',
                                                              'xsl',
                                                              'docbook2pageobject.xsl'))
        if not os.path.exists(xsl_docbook2pageobject):
            raise IOError('%s does not exist' % xsl_docbook2pageobject)

        outputfn = self.d2s.transform('tests/data/xml/book.xml',
                                 xsl_docbook2pageobject)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        # 10 pageobjects expected (2 complex, 8 simple)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 10.0, output)


class CreateScribusDocumentTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

    def testCreateArticle(self):
        """ Test create() function with DocBook article """

        outputfn = self.d2s.create('tests/data/xml/article.xml',
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

        outputfn = self.d2s.create('tests/data/xml/book.xml',
                              'tests/data/scribus/clean134.sla')
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 10.0)

class SyncronizeScribusDocumentTestCase(unittest.TestCase):

    def setUp(self):

        self.d2s = DocBook2Sla()

    def testSyncronizeArticle(self):
        """ Test syncronize() function with DocBook article """
        pass

    def testSyncronizeBook(self):
        """ Test syncronize() function with DocBook book """
        pass

def test_suite():

    suite = unittest.TestLoader().loadTestsFromTestCase(TransformationTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(StylesheetsTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(CreateScribusDocumentTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(SyncronizeScribusDocumentTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return suite

if __name__ == "__main__":
    test_suite()


