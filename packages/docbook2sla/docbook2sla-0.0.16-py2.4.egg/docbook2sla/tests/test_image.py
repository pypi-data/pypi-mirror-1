import os
import sys
import unittest

import tempfile

from lxml import etree
from StringIO import StringIO

from docbook2sla import DocBook2Sla

dirname = os.path.dirname(__file__)

class ImagesTestCase(unittest.TestCase):

    def setUp(self):
        article = """\
<article>
    <mediaobject id="uid001_image_1">
        <imageobject>
            <imagedata fileref="http://localhost:8080/test/example-article-1/internet-mail.png" />
        </imageobject>
        <caption>
            <para>My Second Image</para>
        </caption>
    </mediaobject>
</article>"""

        scribus = os.path.join(os.path.dirname(__file__), 'data', 'scribus', 'clean134.sla')
        #article = os.path.join(os.path.dirname(__file__), 'data', 'xml', 'article+id+image.xml')
        self.d2s = DocBook2Sla()
        outputfn = self.d2s.create(StringIO(article), scribus)
        output = open(outputfn, 'r').read()
        outputtree = etree.XML(output)
        self.output = output
        self.outputtree = outputtree

    def test_no_other_pageobjects(self):
        """ No other pageobjects are existent """
        count_pageobjects = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME!='uid001_image_1'])")
        self.assertEqual(count_pageobjects, 0.0)

    def test_pageobject_exists(self):
        """ Test if image pageobject exists """
        image1 = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='uid001_image_1'])")
        self.assertEqual(image1, 1.0)

    def test_pageobject_attributes(self):
        """ Test attributes """
        ptype = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='uid001_image_1' and @PTYPE='2'])")
        self.assertEqual(ptype, 1.0)

        embedded = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='uid001_image_1' and @EMBEDDED='0'])")
        self.assertEqual(embedded, 1.0)

        irender = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='uid001_image_1' and @IRENDER='0'])")
        self.assertEqual(irender, 1.0)

        pfile = self.outputtree.xpath("count(//PAGEOBJECT[@ANNAME='uid001_image_1' and @PFILE='http://localhost:8080/test/example-article-1/internet-mail.png'])")
        self.assertEqual(pfile, 1.0)

def test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ImagesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    return suite

if __name__ == "__main__":
    test_suite()