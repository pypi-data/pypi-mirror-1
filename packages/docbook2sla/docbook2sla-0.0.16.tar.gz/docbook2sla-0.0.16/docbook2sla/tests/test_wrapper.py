import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class WrapperTestCase(unittest.TestCase):
    """ Test the wrapper stylesheet """

    def setUp(self):

        # create instance
        self.d2s = DocBook2Sla()

        # make stylesheet available
        self.xsl_wrapper = os.path.abspath(os.path.join(dirname, '..', 'xsl', 'wrapper.xsl'))
        if not os.path.exists(self.xsl_wrapper):
            raise IOError('%s does not exist' % self.xsl_wrapper)

        # input
        self.scribus_wrapper = os.path.abspath(os.path.join(dirname, 'data', 'test_wrapper_input.xml'))
        self.pageobjects = os.path.abspath(os.path.join(dirname, 'data', 'test_wrapper_secondinput.xml'))

        # expected
        self.expectedfn = os.path.abspath(os.path.join(dirname, 'data', 'test_wrapper_expected.xml'))
        self.expected = open(self.expectedfn, 'r').read()

        # transform
        self.outputfn = self.d2s.transform(self.scribus_wrapper, self.xsl_wrapper, secondinputfn=self.pageobjects)

        # set output
        self.output = open(self.outputfn, 'r').read()

    def testOutput(self):
        """ Test output """
        pass
        "TODO"
        #self.assertEqual(self.output, self.expected, "%s != %s : %s" % (self.output, self.expected, self.output))

def test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(WrapperTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    return suite

if __name__ == "__main__":
    test_suite()