import os
import sys
import unittest

import tempfile

from docbook2sla import DocBook2Sla

class WrapperTests(unittest.TestCase):

    def testWrapper(self):
        """ Wrapper should generate an id attribute for every xml node.

            xsltproc -o tests/data/testWrapper.output.expected.xml \
                     --stringparam secondinput ../tests/data/testWrapper.input.xml \
                     xsl/wrapper.xsl \
                     tests/data/testWrapper.input.scribus.xml
        """
        d2s = DocBook2Sla()
        outputfn = d2s.wrapper('tests/data/testWrapper.input.xml',
                               'tests/data/testWrapper.input.scribus.xml')
        output = open(outputfn, 'r')
        expected_output = open('tests/data/testWrapper.output.expected.xml', 'r')
        self.assertEqual(output.read(), expected_output.read())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(WrapperTests))
    return suite

if __name__ == "__main__":
    unittest.main()