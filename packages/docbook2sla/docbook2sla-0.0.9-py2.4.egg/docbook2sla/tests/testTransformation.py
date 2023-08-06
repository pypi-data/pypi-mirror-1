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
        pass


    def testTransformation(self):

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.input.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformation.expected.xml')

        print >>sys.stderr, 'testSimpleTransformation: %s, %s' % (inputfn, transformfn)

        d2s = DocBook2Sla()

        # try to transform inputfn
        try:
            outputfn = d2s.transform(inputfn, transformfn)
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
        """ Test transformation with parameters passed.
            xsltproc \
            --stringparam secondinput testTransformationWithParam.secondinput.xml \
            tests/data/testTransformationWithParam.xsl \
            tests/data/testTransformationWithParam.input.xml
        """

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.input.xml')
        secondinputfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.secondinput.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'testTransformationWithParam.expected.xml')

        print >>sys.stderr, 'testTransformationWithParam: %s, %s' % (inputfn, transformfn)

        d2s = DocBook2Sla()

        # try to transform inputfn
        try:
            outputfn = d2s.transform(inputfn, transformfn, secondinputfn=secondinputfn)

        except:
            print >>sys.stderr, 'Error transforming %s with %s' % (inputfn, transformfn)
            raise

        # open output
        output = open(outputfn, 'r').read()

        # open expected output
        expected = open(expectedfn, 'r').read()

        self.assertEqual(output, expected)

        return outputfn


    def testDocBook2PageobjectsArticle(self):
        """ Test transformation from DocBook article to Scribus pageobjects. """

        xsl_docbook2pageobject = os.path.abspath(os.path.join(dirname,
                                                              '..',
                                                              'xsl',
                                                              'docbook2pageobject.xsl'))
        if not os.path.exists(xsl_docbook2pageobject):
            raise IOError('%s does not exist' % xsl_docbook2pageobject)

        d2s = DocBook2Sla()
        outputfn = d2s.transform('tests/data/xml/article.xml',
                                 xsl_docbook2pageobject)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4)


    def testDocBook2PageobjectsBook(self):
        """ Test transformation from DocBook book to Scribus pageobjects. """

        xsl_docbook2pageobject = os.path.abspath(os.path.join(dirname,
                                                              '..',
                                                              'xsl',
                                                              'docbook2pageobject.xsl'))
        if not os.path.exists(xsl_docbook2pageobject):
            raise IOError('%s does not exist' % xsl_docbook2pageobject)

        d2s = DocBook2Sla()
        outputfn = d2s.transform('tests/data/xml/book.xml',
                                 xsl_docbook2pageobject)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)


    def testWrapper(self):
        """ Test the wrapper function. """

        d2s = DocBook2Sla()

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'testWrapper.input.xml')
        secondinputfn = os.path.join(os.path.dirname(__file__), 'data', 'testWrapper.secondinput.xml')
        transformfn = os.path.abspath(os.path.join(dirname, '..', 'xsl', 'wrapper.xsl'))

        outputfn = d2s.transform(inputfn, transformfn, secondinputfn=secondinputfn)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

        # make sure the number of pageobjects is correct
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 2.0)

        # make sure there is a pageobject with id1
        po1 = outputtree.xpath("name(//PAGEOBJECT[@ANNAME='id1'])")
        self.assertEqual(po1, "PAGEOBJECT")

        # make sure there is a pageobject with id2
        po1 = outputtree.xpath("name(//PAGEOBJECT[@ANNAME='id2'])")
        self.assertEqual(po1, "PAGEOBJECT")



    def testCreateArticle(self):
        """ Test create() function with a DocBook article """

        d2s = DocBook2Sla()
        outputfn = d2s.create('tests/data/xml/article.xml',
                              'tests/data/scribus/clean134.sla')
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)

        # make sure the first child of the root node is SCRIBUSUTF8NEW
        root_node = outputtree.xpath("name(/*)")
        self.assertEqual(root_node, "SCRIBUSUTF8NEW")

        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)


    def testCreateBook(self):
        """ Test create() function with a DocBook book """
        d2s = DocBook2Sla()
        outputfn = d2s.create('tests/data/xml/book.xml',
                              'tests/data/scribus/clean134.sla')
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        count_pageobjects = outputtree.xpath("count(//PAGEOBJECT)")
        self.assertEqual(count_pageobjects, 4.0)

#    def testSyncronize(self):
#        d2s = DocBook2Sla()
#        print d2s.syncronize('tests/data/xml/article-1.xml',
#                             'tests/data/output/create_output.sla',
#                             'tests/data/output/syncronize_output.sla')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(makeSuite(TransformationTestCase))
    return suite

if __name__ == "__main__":
    unittest.main()