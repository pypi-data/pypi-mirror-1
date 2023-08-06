# -*- coding: iso-8859-1

###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import unittest, sys
from zopyx.txng3.splitter import Splitter

class SplitterTests(unittest.TestCase):

    def testSimple(self):
        
        SP = Splitter()
        self._test(SP, '',  [])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u' foo ', [u'foo'])
        self._test(SP, u' foo bar', [u'foo',u'bar'])
        self._test(SP, u' foo bar ', [u'foo',u'bar'])
        self._test(SP, u' foo 23 25 bar ', [u'foo',u'23', u'25',u'bar'])

    def testDisabledCaseFolding(self):

        SP = Splitter(casefolding=0)
        self._test(SP, u'',  [])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u' Foo ',  [u'Foo'])
        self._test(SP, u' Foo Bar', [u'Foo',u'Bar'])
        self._test(SP, u' foo Bar ', [u'foo',u'Bar'])


    def testEnabledCaseFolding(self):

        SP = Splitter(casefolding=1)

        self._test(SP, u'',  [])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u'foo',  [u'foo'])
        self._test(SP, u' Foo ',  [u'foo'])
        self._test(SP, u' Foo Bar', [u'foo',u'bar'])
        self._test(SP, u' foo Bar ', [u'foo',u'bar'])

    def testMaxlen(self):
        
        SP = Splitter(maxlen=5)
        self._test(SP, u'abcdefg foo barfoo', [u'abcde',u'foo',u'barfo'])
        self._test(SP, u'abcdefg'*2000, [u'abcde'])

    def testSeparator1(self):

        SP = Splitter(separator=".-")
        self._test(SP, u'foo 22.33 bar',  [u'foo',u'22.33',u'bar'])
        self._test(SP, u'foo 22-33 bar',  [u'foo',u'22-33',u'bar'])
        self._test(SP, u'foo 22_33 bar',  [u'foo',u'22','33',u'bar'])

    def testSeparator2(self):
        SP = Splitter(separator=".")
        self._test(SP, u'end 12.12 line', [u'end',u'12.12',u'line'])
        self._test(SP, u'end of. line.foo end.', [u'end',u'of',u'line.foo',u'end'])
        self._test(SP, u'end of. line', [u'end',u'of',u'line'])

    def testSeparator3(self):
        SP = Splitter(separator="+_-")
        self._test(SP, u'test c++ hello-world bar', 
                      [u'test', u'c++', u'hello-world', u'bar'])


    def testSingleChars(self):
        SP = Splitter(singlechar=1)
        self._test(SP, u'ab a b c',  [u'ab',u'a',u'b',u'c'])
        self._test(SP, u'foo 2 2 bar ', [u'foo',u'2',u'2',u'bar'])

    def testGerman(self):

        SP = Splitter(singlechar=1)
        self._test(SP, u'der bäcker Ging über die Brücke',
                       [u'der',u'bäcker',u'ging',u'über',u'die',u'brücke'])

        self._test(SP, 'der äücker Ging über die Brücke',
                       [u'der',u'äücker',u'ging',u'über',u'die',u'brücke'])

    def testSwedish(self):

        SP = Splitter(singlechar=1)
        self._test(SP,  u'åke  vill ju inte alls leka med mig.',
                       [u'åke',u'vill',u'ju',u'inte',u'alls', u'leka',u'med',u'mig'])

    def testParagraphs(self):
        SP = Splitter(singlechar=1, separator='§')
        
        self._test(SP, u'dies ist §8 b b§b',
                       [u'dies', u'ist', u'§8', u'b', u'b§b'])


    def _test(self, SP, text, expected):
        got = SP.split(text)
        self.assertEqual(got, expected)


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(SplitterTests))
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

