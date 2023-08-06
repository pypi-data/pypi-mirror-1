###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import sys, os, unittest, gzip
from zopyx.txng3.stemmer import Stemmer


__basedir__ = os.path.dirname(__file__)

class SimpleStemmerTests(unittest.TestCase):

    def getData(self, lang):

        voc = gzip.open(os.path.join(__basedir__, lang, 'voc.txt.gz')).read()
        out = gzip.open(os.path.join(__basedir__, lang, 'output.txt.gz')).read()

        voc = [ x.strip() for x in voc.split('\n') ]
        out = [ x.strip() for x in out.split('\n') ]

        assert len(voc) == len(out)
        return voc, out


    def doTest(self, language, encoding):
        """ simple stemming"""

        S = Stemmer(language)
        voc, out = self.getData(language)

        for v,r  in zip(voc,out):
            r = unicode(r, encoding)
            v = unicode(v, encoding)
            self.assertEqual(S.stem([v]), [r], 'term: %s\ngot: %s\nexpected: %s' % (repr(v), repr(S.stem([v])), repr(r)))


        voc = [unicode(t, encoding) for t in voc]
        out = [unicode(t, encoding) for t in out]
        self.assertEqual(S.stem(voc), out)

    def testGerman(self):
        self.doTest('german', 'iso-8859-15')

    def testFrench(self):
        self.doTest('french', 'iso-8859-15')

    def testDanish(self):
        self.doTest('danish', 'iso-8859-15')

    def testDutch(self):
        self.doTest('dutch', 'iso-8859-15')

    def testEnglish(self):
        self.doTest('english', 'iso-8859-15')

    def testDanish(self):
        self.doTest('danish', 'iso-8859-15')

    def testItalian(self):
        self.doTest('italian', 'iso-8859-15')

    def testNorwegian(self):
        self.doTest('norwegian', 'iso-8859-15')

    def testPortuguese(self):
        self.doTest('portuguese', 'iso-8859-15')

    def testSpanish(self):
        self.doTest('spanish', 'iso-8859-15')

    def testSwedisch(self):
        self.doTest('swedish', 'iso-8859-15')

    def testRussian(self):
        self.doTest('russian', 'koi8-r')

    def testPorter(self):
        self.doTest('porter', 'iso-8859-15')

    def testFinnish(self):
        self.doTest('finnish', 'iso-8859-15')

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(SimpleStemmerTests))
    return s

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

