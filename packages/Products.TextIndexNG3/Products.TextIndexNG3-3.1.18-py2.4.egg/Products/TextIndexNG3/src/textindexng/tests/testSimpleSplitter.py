# -*- coding: iso-8859-1

###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import unittest, sys

from zope.interface.verify import verifyClass

from textindexng.splitter import SimpleSplitter
from textindexng.interfaces import ISplitter

class SimpleSplitterTests(unittest.TestCase):

    def _test(self, S, text, expected):
        got = S.split(text)
        if list(got) != list(expected):
            raise AssertionError('\nText: %s\nGot:      %r\nExpected: %r' % (text, got, expected))

    def testInterface(self):
        verifyClass(ISplitter, SimpleSplitter)

    def testSimple(self):
        
        SP = SimpleSplitter()
        self._test(SP, '',  [])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, ' foo ', ['foo'])
        self._test(SP, ' foo bar', ['foo','bar'])
        self._test(SP, ' foo bar ', ['foo','bar'])
        self._test(SP, ' foo 23 25 bar ', ['foo','23','25','bar'])

    def testDisabledCaseFolding(self):

        SP = SimpleSplitter(casefolding=0)
        self._test(SP, '',  [])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, ' Foo ',  ['Foo'])
        self._test(SP, ' Foo Bar', ['Foo','Bar'])
        self._test(SP, ' foo Bar ', ['foo','Bar'])


    def testEnabledCaseFolding(self):

        SP = SimpleSplitter(casefolding=1)

        self._test(SP, '',  [])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, 'foo',  ['foo'])
        self._test(SP, ' Foo ',  ['foo'])
        self._test(SP, ' Foo Bar', ['foo','bar'])
        self._test(SP, ' foo Bar ', ['foo','bar'])

    def testGerman(self):

        SP = SimpleSplitter()
        self._test(SP, 'der bäcker Ging über die Brücke',
                       ['der','bäcker','ging','über','die','brücke'])

        self._test(SP, 'der äücker Ging über die Brücke',
                       ['der','äücker','ging','über','die','brücke'])

    def testPunctuation(self):
        SP = SimpleSplitter()
        self._test(SP, 'der mann, der über die Brücke ging.',
                       ['der','mann','der','über','die','brücke', 'ging'])
        SP = SimpleSplitter(punctuation='\.')
        self._test(SP, 'der mann, der über die Brücke ging.',
                       ['der','mann,','der','über','die','brücke', 'ging'])


    def testSwedish(self):

        SP = SimpleSplitter()
        self._test(SP, 'åke  vill ju inte alls leka med mig.',
                       ['åke','vill','ju','inte','alls','leka','med','mig'])

    def testPunctuation(self):
        SP = SimpleSplitter()
        self._test(SP, 'a! bc: 3d',
                       ['a', 'bc', '3d'])

    def testObscure(self):

        SP = SimpleSplitter()
        self._test(SP, '', [])
        self._test(SP, ' ', [])
        self._test(SP, '  ', [])
        self._test(SP, ' , ', [])
        self._test(SP, ' x  x  ', ['x', 'x'])


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(SimpleSplitterTests))
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

