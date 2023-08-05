import os
import sys
import unittest

import tempfile

from docbook2sla import DocBook2Sla

class GenerateIdTests(unittest.TestCase):

    def testGenerateId(self):
        """ generateId should generate an id attribute for every xml node.

            xsltproc -o tests/data/testGenerateId.output.expected.xml \
                     xsl/generate-id.xsl \
                     tests/data/testGenerateId.input.xml
        """
        d2s = DocBook2Sla()
        outputfn = d2s.generateId('tests/data/testGenerateId.input.xml')
        output = open(outputfn, 'r')
        expected_output = open('tests/data/testGenerateId.output.expected.xml', 'r')
        self.assertEqual(output.read(), expected_output.read())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(GenerateIdTests))
    return suite

if __name__ == "__main__":
    unittest.main()