import os
import sys
import unittest

import tempfile

from docbook2sla import DocBook2Sla

class TransformationTests(unittest.TestCase):

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

#    def testCreate(self):
#        """ test"""
#        d2s = DocBook2Sla()
#        print d2s.create('tests/data/xml/content.xml',
#                         'tests/data/scribus/clean134.sla',
#                         'tests/data/output/create_output.sla')

#    def testSyncronize(self):
#        d2s = DocBook2Sla()
#        print d2s.syncronize('tests/data/xml/content.xml',
#                             'tests/data/output/create_output.sla',
#                             'tests/data/output/syncronize_output.sla')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TransformationTests))
    return suite

if __name__ == "__main__":
    unittest.main()
