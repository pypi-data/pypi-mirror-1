import os
import sys
import unittest

from zope.interface.verify import verifyClass

import tempfile
from docbook2sla.interfaces import IDocBook2Sla
from docbook2sla.docbook2sla import DocBook2Sla

docbook1        = os.path.join(os.path.dirname(__file__), 'data', 'docbook1.xml')
scribus1        = os.path.join(os.path.dirname(__file__), 'data', 'scribus1.sla')
transform       = os.path.join(os.path.dirname(__file__), 'data', 'merge.xsl')
expected_result = os.path.join(os.path.dirname(__file__), 'data', 'expected_result.sla')

class ConverterTests(unittest.TestCase):

    def testInterfaces(self):
        verifyClass(IDocBook2Sla, DocBook2Sla)

class RegressionTests(unittest.TestCase):

    def testConversion(self):

        print >>sys.stderr, 'Param: %s, %s, %s' % (docbook1, scribus1, transform)
        try:
            output_filename = DocBook2Sla().convert(docbook1, scribus1, transform, 'output1.sla')
        except:
            print >>sys.stderr, 'Error converting %s and %s with %s' % (docbook1, scribus1, transform)
            raise

        datei = open(output_filename, 'r')
        zeilen = []
        while 1:
            zeile = datei.readline()
            if zeile == '':
                break
            zeilen.append(zeile)
        datei.close()
        print >>sys.stderr, 'Output: %s' % zeilen

    def testSimplePageobject(self):
        """
        """
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ConverterTests))
    suite.addTest(makeSuite(RegressionTests))
    return suite

if __name__ == "__main__":
    unittest.main()
