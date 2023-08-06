# -*- coding: iso-8859-15 -*-

###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, unittest, os

from textindexng.converters import html, sgml, ooffice, pdf


class ConverterTests(unittest.TestCase):

    def testHTML(self):
        doc = '<html><body> alle V�gel �ber Fl�gel und T�mpel</body></html>'
        utf8doc = unicode('alle V�gel �ber Fl�gel und T�mpel', 'iso-8859-15').encode('utf-8')
        C = html.Converter()
        text,enc = C.convert(doc, 'iso-8859-15', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        doc1 = unicode(doc, 'iso-8859-15').encode('utf-8')         
        text, enc= C.convert(doc1, 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        doc2 = unicode(doc, 'iso-8859-15')
        text, enc= C.convert(doc2, 'unicode', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)
        
        
    def testHTMLWithEntities(self):
        doc = '<html><body> alle V&ouml;gel &Uuml;ber Fl&uuml;gel und T&uuml;mpel</body></html>'
        utf8doc = unicode('alle V�gel �ber Fl�gel und T�mpel', 'iso-8859-15').encode('utf-8')

        C = html.Converter()
        text,enc = C.convert(doc, 'iso-8859-15', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        doc1 = unicode(doc, 'iso-8859-15').encode('utf-8')         
        text, enc= C.convert(doc1, 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

    def testXML(self):
        doc = '<?xml version="1.0" encoding="iso-8859-15" ?><body> alle V�gel �ber Fl�gel und T�mpel</body>'
        utf8doc = unicode('alle V�gel �ber Fl�gel und T�mpel', 'iso-8859-15').encode('utf-8')

        C = sgml.Converter()
        # encoding should be taken from the preamble
        text,enc = C.convert(doc, 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

    def testOpenOffice(self):
        doc = open(os.path.join(os.path.dirname(__file__), 'data', 'test.sxw')).read()

        C = ooffice.Converter()
        # encoding should be taken from the preamble
        text, enc = C.convert(doc, 'utf8', 'text/html')
        expected = 'Viel V�gel sprangen artig in den T�pel und �ber Feld und W�ste'
        expected_words = [w.strip() for w in unicode(expected, 'iso-8859-15').encode(enc).split() if w.strip()]
        got_words = [w.strip() for w in text.split() if w.strip()]
        self.assertEqual(got_words, expected_words)

    def testPDF(self):
        doc = open(os.path.join(os.path.dirname(__file__), 'data', 'test.pdf')).read()

        C = pdf.Converter()
        # encoding should be taken from the preamble
        text, enc = C.convert(doc, 'utf8', 'text/html')
        expected = 'Viel V�gel sprangen artig in den T�pel und �ber Feld und W�ste'
        expected_words = [w.strip() for w in unicode(expected, 'iso-8859-15').encode(enc).split() if w.strip()]
        got_words = [w.strip() for w in text.split() if w.strip()]
        self.assertEqual(got_words, expected_words)

def test_suite():
   return unittest.makeSuite(ConverterTests)

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

