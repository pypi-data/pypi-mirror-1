#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, os, unittest

from Interface.Verify import verifyClass
from OFS.DTMLDocument import addDTMLDocument

from Products.TextIndexNG3 import package_home
from Products.TextIndexNG3.TextIndexNG3 import TextIndexNG3
from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface

from txngtest import TextIndexNG3TestCase
from textindexng.config import *
from textindexng.resultset import ResultSet


class TextIndexNG3Tests(TextIndexNG3TestCase):


    def afterSetUp(self):
        factory = self.folder.manage_addProduct['ZCatalog']
        factory.manage_addZCatalog('catalog', 'catalog')
        catalog = self.folder['catalog']
        
    def testInterfaceMock(self):
        verifyClass(PluggableIndexInterface, TextIndexNG3)

    def testSimpleSetup(self):
        extra = {'lexicon' : DEFAULT_LEXICON,
                 'storage' : DEFAULT_STORAGE,
                 'splitter' : DEFAULT_SPLITTER}
        self.folder.catalog.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG3', extra)

    def testStemmer(self):
        extra = {'use_stemmer' : True}
        self.folder.catalog.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG3', extra)
        idx = self.folder.catalog.Indexes['PrincipiaSearchSource']
        self.assertEqual(idx.index.use_stemmer, True)

        extra = {'use_stemmer' : False}
        self.folder.catalog.manage_addIndex('PrincipiaSearchSource1', 'TextIndexNG3', extra)
        idx = self.folder.catalog.Indexes['PrincipiaSearchSource1']
        self.assertEqual(idx.index.use_stemmer, False)
    
    def testIndexing(self):
        extra = {'lexicon' : DEFAULT_LEXICON,
                 'storage' : DEFAULT_STORAGE,
                 'splitter' : DEFAULT_SPLITTER}
        self.folder.catalog.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG3', extra)
        datadir = os.path.join(package_home, 'src', 'textindexng', 'tests', 'data', 'texts')
        for f in os.listdir(datadir):
            fname = os.path.join(datadir, f)
            if not os.path.isfile(fname): continue
            fp = open(fname) 
            addDTMLDocument(self.folder, id=f, title=f, file=fp)
            fp.close()

        for obj in [o for o in self.folder.objectValues('DTML Document') if o.getId().endswith('txt')]:
            self.folder.catalog.catalog_object(obj, obj.absolute_url(1))
        self.assertEqual(len(self.folder.catalog), 199)

    def test_apply_index(self):
        self.folder.catalog.manage_addIndex('foo', 'TextIndexNG3')
        idx = self.folder.catalog.Indexes['foo']
        def dummysearch(query, **kw):
            return ResultSet((query, kw), None)
        idx.index.search = dummysearch

        request = {}
        self.assertEqual(idx._apply_index(request), None)

        request = {'foo': 'Foo'}
        self.assertEqual(idx._apply_index(request)[0][0], u'Foo')
        self.assertEqual(idx._apply_index(request)[0][1], {})

        request = {'foo': {'query': 'Foo'}}
        self.assertEqual(idx._apply_index(request)[0][0], u'Foo')
        self.assertEqual(idx._apply_index(request)[0][1], {})

        request = {'foo': {'query': 'Foo', 'parser': 'foo_parser'}}
        self.assertEqual(idx._apply_index(request)[0][0], u'Foo')
        self.assertEqual(idx._apply_index(request)[0][1],
                         {'parser': 'foo_parser'})

        request = {'foo': {'query': 'Foo', 'ranking': False}}
        self.assertEqual(idx._apply_index(request)[0][0], u'Foo')
        self.assertEqual(idx._apply_index(request)[0][1],
                         {'ranking': False})


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TextIndexNG3Tests))
    return s

def main():
    unittest.TextTestRunner().run(test_suite())
    pass

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

