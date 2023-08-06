import os
import sys
import unittest

import tempfile

from docbook2sla import DocBook2Sla

class DocBook2PageobjectsTests(unittest.TestCase):

    def testDocBook2Pageobjects(self):
        """ . """
        d2s = DocBook2Sla()
        outputfn = d2s.docbook2Pageobjects('tests/data/testDocBook2Pageobjects.input.xml')
        output = open(outputfn, 'r')
        expected_output = open('tests/data/testDocBook2Pageobjects.output.expected.xml', 'r')
        self.assertEqual(output.read(), expected_output.read())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DocBook2PageobjectsTests))
    return suite

if __name__ == "__main__":
    unittest.main()