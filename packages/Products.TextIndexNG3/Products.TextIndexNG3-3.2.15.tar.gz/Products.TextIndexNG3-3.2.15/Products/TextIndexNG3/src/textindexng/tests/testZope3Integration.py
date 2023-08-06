#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
zope3 integration unit tests

$Id: testZope3Integration.py 1911 2008-01-20 18:20:04Z ajung $
"""

import os, sys, glob, random, unittest

from zope.interface import implements
from zope.interface.verify import verifyClass
from zope.app.testing import ztapi
import zope.component

from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.catalog import Catalog
import zope.app.catalog.text
import zope.app.catalog.interfaces

from TextIndexNGTestCase import TextIndexNGTestCase
from textindexng.ting import TingIndex 
from textindexng.interfaces import IIndexableContent
from textindexng.content import extract_content

import mock

class Zope3IntegrationTest(TextIndexNGTestCase):

    def testImplements(self):
        verifyClass(zope.app.catalog.text.ITextIndex, TingIndex)
        verifyClass(zope.app.catalog.interfaces.IAttributeIndex, TingIndex)
        verifyClass(IIndexableContent, mock.Mock)

    def testIntegration(self):
        stupid = mock.Mock(language='en', text=u'dummytext')
        ting = TingIndex(field_name='text', interface=IIndexableContent)
        content = extract_content(ting._index.fields, stupid, default_language='en')
        self.failUnless(content)
        self.failUnless(ting.documentCount()==0)
        ting.index_doc(1, stupid)
        self.failUnless(ting.documentCount()==1)
        result = ting.apply({'query' : u'dummytext', 'field' : 'text', 'language' : 'en'})
        self.failUnless(len(result)==1)
        ting.unindex_doc(1)
        self.failUnless(ting.documentCount()==0)

    def testCatalogIntegration(self):
        """ test how the index layer behaves in catalog """

        catalog = Catalog()
        ztapi.provideUtility(zope.app.catalog.interfaces.ICatalog, catalog)

        intids = IntIds()
        ztapi.provideUtility(IIntIds, intids)

        catalog['text'] = TingIndex(field_name='text', interface=IIndexableContent, field_callable=False)
        stupid = mock.Mock(language='en', text=u'andi is a YETI')
        catalog.index_doc(42, stupid)
        results = catalog.searchResults(text=u'andi*')
        self.failUnless(len(results) == 1)
        results = catalog.searchResults(text=u'*andi')
        self.failUnless(len(results) == 1)
        self.failUnless(results.__dict__.has_key('uids'))

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(Zope3IntegrationTest))
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
