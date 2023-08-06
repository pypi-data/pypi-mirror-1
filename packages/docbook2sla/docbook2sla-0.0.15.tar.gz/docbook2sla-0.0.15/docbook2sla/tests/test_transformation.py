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

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformation.input.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformation.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformation.expected.xml')

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

        inputfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformationWithParam.input.xml')
        secondinputfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformationWithParam.secondinput.xml')
        transformfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformationWithParam.xsl')
        expectedfn = os.path.join(os.path.dirname(__file__), 'data', 'test_transformation', 'testTransformationWithParam.expected.xml')

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

def test_suite():

    suite = unittest.TestLoader().loadTestsFromTestCase(TransformationTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return suite

if __name__ == "__main__":
    test_suite()


