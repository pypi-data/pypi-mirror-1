#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, os, unittest

from zope.interface import implements        
from zope.interface.verify import verifyClass
from zope.app.tests import ztapi

from textindexng.index import Index
from textindexng.config import DEFAULT_LANGUAGE
from textindexng.content import extract_content, IndexContentCollector
from textindexng.interfaces import IIndex, IIndexContentCollector, IIndexableContent, IObjectWrapper

from TextIndexNGTestCase import TextIndexNGTestCase
from mock import Mock, MockPDF, MockOld, StupidMock, StupidMockAdapter, IStupidMock
from texts import de1, de2, de3, en1, en2, en3, fr1, fr2, fr3


class ContentCollectorTests(TextIndexNGTestCase):

    def testInterface(self):
        verifyClass(IIndexContentCollector, IndexContentCollector)


class ContentExtractionTests(TextIndexNGTestCase):

    def testInterfaceMock(self):
        verifyClass(IIndexableContent, Mock)
        verifyClass(IIndexableContent, MockPDF)

    def testObjectsImplementingITextIndexable(self):
        o = Mock(SearchableText=u'The quick brown fox jumps over the lazy dog', language='en')
        d = extract_content(('SearchableText',), o)
        data = d.getFieldData('SearchableText')
        self.assertEqual(data['content'], u'The quick brown fox jumps over the lazy dog')
        self.assertEqual(data['language'],'en')
        o = Mock(SearchableText=u'The quick brown fox jumps over the lazy dog', language='en')
        d = extract_content(('searchabletext',), o)
        self.assertEqual(d, None)


    def testObjectWrapper(self):
        """ same test a testObjectImplementingITextIndexable() except
            the object to be indexed is packed inside a Wrapper.
        """
    
        class Wrapper:

            implements(IObjectWrapper)

            def __init__(self, ob):
                self.ob = ob

            def getWrappedObject(self):
                return self.ob

        o = Mock(SearchableText=u'The quick brown fox jumps over the lazy dog', language='en')
        o = Wrapper(o)
        d = extract_content(('SearchableText',), o)
        data = d.getFieldData('SearchableText')
        self.assertEqual(data['content'], u'The quick brown fox jumps over the lazy dog')
        self.assertEqual(data['language'],'en')
        o = Mock(SearchableText=u'The quick brown fox jumps over the lazy dog', language='en')
        d = extract_content(('searchabletext',), o)
        self.assertEqual(d, None)

    def testObjectsImplementingITextIndexableRaw(self):
        o = MockPDF('data/test.pdf')
        d = extract_content(('SearchableText',), o, True)
        self.assertEqual('SearchableText' in d.getFields(), True)
        d = extract_content(('searchabletext',), o, True)
        self.assertEqual(d, None)

    def testObjectImplementingOldZopeTwoAPI(self):
        o = MockOld()
        icc = extract_content(('SearchableText',), o)
        d = icc.getFieldData('SearchableText')
        self.assertEqual(d['content'], u'The quick brown fox jumps over the lazy dog')
        self.assertEqual(d['language'], DEFAULT_LANGUAGE)
        icc  = extract_content(('text',), o)
        d = icc.getFieldData('text')
        self.assertEqual(d['content'], u'The quick brown fox jumps over the lazy dog')
        self.assertEqual(d['language'], DEFAULT_LANGUAGE)
        icc = extract_content(('searchabletext',), o)
        self.assertEqual(icc, None)

    def testStupidMockWithAdapter(self):
        # this test checks if we can extract content from stupid objects not implementing
        # the TXNG interfaces through adapters
        ztapi.provideAdapter(IStupidMock, IIndexableContent, StupidMockAdapter)
        o = StupidMock(SearchableText='god save the queen komma acht komma eins', language='en')
        d = extract_content(('SearchableText',), o, True)
        self.assertEqual(d.getFieldData('SearchableText')['content'], 'i am so stupid')

class ProcessingPipelineTests(TextIndexNGTestCase):

    def _test(self, index, input, expected, language='en'):
        result = index._process_words(input, language)
        if list(result) != list(expected):
            raise AssertionError('\nProcessing: %s\nIndex: %s\nGot:      %s\nExpected: %s' % (repr(input), repr(index), repr(result), repr(expected)))             
    def testEmpty(self):
        I = Index(fields=('oo',))
        self._test(I, u'', ())

    def testSplitter(self):
        I = Index(splitter_casefolding=False, fields=('foo',))
        self._test(I, u'a B c', ('a', 'B', 'c'))
        self._test(I, u'foo bAR', ('foo', 'bAR'))
        I = Index(splitter_casefolding=True, fields=('foo',))
        self._test(I, u'a B c', ('a', 'b', 'c'))
        self._test(I, u'foo bAR', ('foo', 'bar'))
        
    def testStopWords(self):
        I = Index(splitter_casefolding=True, use_stopwords=False, fields=('foo',))
        self._test(I, u'the black blue fox', ('the', 'black', 'blue', 'fox'))
        I = Index(splitter_casefolding=True, use_stopwords=True, fields=('foo',))
        self._test(I, u'the black blue fox', ('black', 'blue', 'fox'), 'en')
        self._test(I, u'das Auto auf dem garten', ('das', 'auto', 'auf', 'dem', 'garten'), 'en')
        self._test(I, u'das Auto auf dem garten', ('das', 'auto', 'auf', 'dem', 'garten'), 'xx')
        self._test(I, u'das Auto auf dem garten', ('auto', 'garten'), 'de')

    def testNormalizer(self):
        I = Index(splitter_casefolding=True, use_stopwords=False, use_normalizer=True, fields=('foo',))
        self._test(I, u'für und über drüben gehen Wir', (u'fuer', u'und', u'ueber', u'drueben', u'gehen', u'wir'), 'de')
        self._test(I, u'fÜr und über drÜben gehen Wir', (u'fuer', u'und', u'ueber', u'drueben', u'gehen', u'wir'), 'de')
        self._test(I, u'für und über drüben gehen Wir', (u'für', u'und', u'über', u'drüben', u'gehen', u'wir'), 'en')


class IndexTests(TextIndexNGTestCase):

    def testInterface(self):
        verifyClass(IIndex, Index)

    def testSettings(self):
        I = Index(fields=('foo',))
        self.assertEqual(I.splitter, 'txng.splitters.default')

    def testEmptyQuery(self):
        I = Index(fields=('foo',))
        self.assertRaises(ValueError, I.search, query='')

    def testIndexWithMultipleLanguages(self):
        o1 = Mock(text=u'The quick brown fox', language='en')
        o2 = Mock(text=u'der schnelle braune fuchs', language='de')
        o3 = Mock(text=u'je ne sais pas', language='fr')
        I = Index(fields=('text',), dedicated_storage=True, languages=('de', 'en'), index_unknown_languages=False)
        I.index_object(o1, 1)
        I.index_object(o2, 2)
        self.assertRaises(ValueError, I.index_object, o3, 3)
        en_words = I._lexicon.getWordsForLanguage('en')
        en_words.sort()
        de_words = I._lexicon.getWordsForLanguage('de')
        de_words.sort()
        self.assertEqual(en_words, ['brown', 'fox', 'quick', 'the'])
        self.assertEqual(de_words, ['braune', 'der', 'fuchs', 'schnelle'])

    def testIndexWithOneLanguage(self):
        o1 = Mock(text=u'The quick brown fox', language='en')
        o2 = Mock(text=u'der schnelle braune fuchs', language='de')
        o3 = Mock(text=u'je ne sais pas', language='fr')
        I = Index(fields=('text',), dedicated_storage=True, languages=('en',), index_unknown_languages=False)
        I.index_object(o1, 1)
        self.assertRaises(ValueError, I.index_object, o2, 2)
        self.assertRaises(ValueError, I.index_object, o2, 3)
        en_words = I._lexicon.getWordsForLanguage('en')
        en_words.sort()
        self.assertEqual(en_words, ['brown', 'fox', 'quick', 'the'])

    
class StemmerTests(TextIndexNGTestCase):

    def setupIndex(self, index):
        TextIndexNGTestCase.setUp(self)
        index.index_object(Mock('de', text=unicode(de1, 'iso-8859-15')), 1)

    def _test(self, index, query, language, expected, field='text'):
        res = index.search(query, language=language, field=field)        
        docids = list(res.getDocids())
        docids.sort()
        expected = list(expected)
        expected.sort()
        if docids != expected:
            raise AssertionError('Query failed (%s/%s): %s\nGot:     %s\nExpected: %s' % (field, language, query, docids, expected))            


    def testGermanStemmer(self):
        I = Index(fields=('text',), languages=('de', 'fr', 'en'), use_stemmer=True)
        self.setupIndex(I)
        self._test(I, u'Gleich ihr', 'de', (1,))
        self._test(I, u'Gleiche ihren', 'de', (1,))
        self._test(I, u'existentiellen Eigentlichen', 'de', (1,))
        self._test(I, u'existentiell Eigentlich', 'de', (1,))
        self._test(I, u'"existentiellen Eigentlichen"', 'de', (1,))
        self._test(I, u'"existentiell Eigentlicher"', 'de', (1,))
        self._test(I, u'"existentiell Eigentliche"', 'de', (1,))
        # enabled stemming -> no wildcard searches supported
        self.assertRaises(ValueError, I.search, 'existentiell*') 
        self.assertRaises(ValueError, I.search, 'existent?foo') 
        self.assertRaises(ValueError, I.search, '*a') 

    
class MultilingualTests(TextIndexNGTestCase):

    def setupIndex(self, index):
        TextIndexNGTestCase.setUp(self)
        index.index_object(Mock('de', text=unicode(de1, 'iso-8859-15')), 1)
        index.index_object(Mock('de', text=unicode(de2, 'iso-8859-15')), 2)
        index.index_object(Mock('de', text=unicode(de3, 'iso-8859-15')), 3)
        index.index_object(Mock('fr', text=unicode(fr1, 'iso-8859-15')), 4)
        index.index_object(Mock('fr', text=unicode(fr2, 'iso-8859-15')), 5)
        index.index_object(Mock('fr', text=unicode(fr3, 'iso-8859-15')), 6)
        index.index_object(Mock('en', text=unicode(en1, 'iso-8859-15')), 7)
        index.index_object(Mock('en', text=unicode(en2, 'iso-8859-15')), 8)
        index.index_object(Mock('en', text=unicode(en3, 'iso-8859-15')), 9)

    def _test(self, index, query, language, expected, field='text'):
        res = index.search(query, language=language, field=field)        
        docids = list(res.getDocids())
        docids.sort()
        expected = list(expected)
        expected.sort()
        if docids != expected:
            raise AssertionError('Query failed (%s/%s): %s\nGot:     %s\nExpected: %s' % (field, language, query, docids, expected))            

    def testSetup(self):
        I = Index(fields=('text',), languages=('de', 'fr', 'en'))
        self.setupIndex(I)

    def testDE(self):
        I = Index(fields=('text',), languages=('de', ), index_unknown_languages=False)
        I.index_object(Mock('de', text=unicode(de1, 'iso-8859-15')), 1)
        # this raises an exception because the index does not know about 'fr' or 'en'
        self.assertRaises(ValueError, I.index_object, Mock('fr', text=unicode(fr1, 'iso-8859-15')), 4)
        self.assertRaises(ValueError, I.index_object, Mock('en', text=unicode(en1, 'iso-8859-15')), 5)

    def testSingleLanguageDependentSearches(self):
        I = Index(fields=('text',), languages=('de', 'fr', 'en'))
        self.setupIndex(I)
        self._test(I, u'Gleich ihr', 'de', (1,))
        self._test(I, u'sich', 'de', (1, 2, 3))
        self._test(I, u'"an sich"', 'de', (3, ))
        self._test(I, u'"an sich"', 'fr', ())
        self._test(I, u'"YXXX YYY"', 'de', ())
        self._test(I, u'emanzipation ', 'de', (2,3))
        self._test(I, u'"denken zur emanzipation" not selbsterhaltung', 'de', ())
        self._test(I, u'"conceptualist"', 'en', (7,9,))
        self._test(I, u'emanzipation -denken', 'de', (3,))
        self._test(I, u'emanzipation not denken', 'de', (3,))
        self._test(I, u'emanzipation and not denken', 'de', (3,))
        self._test(I, u'not denken and emanzipation ', 'de', (3,))
        self._test(I, u'"that we have to choose between postpatriarchial conceptualist theory textual and objectivism"', 'en', ())
        self._test(I, u'"that we have to choose between postpatriarchial conceptualist theory and textual objectivism"', 'en', (9,))

    def testMultipleFieldsMultipleLanguages(self):
        I = Index(fields=('text','author'), languages=('de', 'fr', 'en'))
        I.index_object(Mock('de', text=unicode(de1, 'iso-8859-15'), author=u'Andreas Jung'), 1)
        I.index_object(Mock('de', text=unicode(de2, 'iso-8859-15'), author=u'Andrea Jung'), 2)
        I.index_object(Mock('de', text=unicode(de3, 'iso-8859-15'), author=u'der Nasbär'), 3)
        self._test(I, u'andreas jung', 'en', ())
        self._test(I, u'andreas jung', 'de', ())
        self._test(I, u'andreas jung', 'de', (1,), 'author')
        self._test(I, u'jung   andreas', 'de', (1,), 'author')
        self._test(I, u'"jung   andreas"', 'de', (), 'author')
        self._test(I, u'"andreas jung"', 'de', (1,), 'author')
        self._test(I, u'andrea jung', 'de', (2,), 'author')
        self._test(I, u'andreas jung', 'de', (1,), 'author')
        self._test(I, u'na*', 'de', (3,), 'author')
        
    def testWithAndWithoutStopwords(self):
        I = Index(fields=('text',), languages=('de', 'fr', 'en'), use_stopwords=False)
        self.setupIndex(I)
        self._test(I, u'das opfer wird uns frei machen', 'de', (1,))

        I = Index(fields=('text',), languages=('de', 'fr', 'en'), use_stopwords=True)
        self.setupIndex(I)
        # This should give a hit since 'das' should be filtered from the query
        self._test(I, u'das opfer wird uns frei machen', 'de', (1,))
        self._test(I, u'DaS opfer wird uns frei machen', 'de', (1,))

    def testIndexAndUnindex(self):
        I = Index(fields=('text','author'), languages=('de', 'fr', 'en'))
        I.index_object(Mock('de', text=unicode(de1, 'iso-8859-15'), author=u'Andreas Jung'), 1)
        I.index_object(Mock('de', text=unicode(de2, 'iso-8859-15'), author=u'Andrea Jung'), 2)
        I.index_object(Mock('de', text=unicode(de3, 'iso-8859-15'), author=u'der Nasbär'), 3)
        self._test(I, u'andreas jung', 'de', (1,), 'author')
        I.unindex_object(1)
        I.unindex_object(2)
        I.unindex_object(3)
        I.unindex_object(9999)
        self._test(I, u'andreas jung', 'de', (), 'author')
        I.index_object(Mock('de', text=unicode(de1, 'iso-8859-15'), author=u'Andreas Jung'), 1)
        self._test(I, u'andreas jung', 'de', (1,), 'author')
        self._test(I, u'andreas jung', 'de', (), 'text')
        self._test(I, u'das opfer wird', 'de', (1,), 'text')
        I.index_object(Mock('de', text=unicode(de2, 'iso-8859-15'), author=u'Andrea Jung'), 1)
        self._test(I, u'andrea jung', 'de', (1,), 'author')

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ContentCollectorTests))
    s.addTest(unittest.makeSuite(ContentExtractionTests))
    s.addTest(unittest.makeSuite(ProcessingPipelineTests))
    s.addTest(unittest.makeSuite(IndexTests))
    s.addTest(unittest.makeSuite(StemmerTests))
    s.addTest(unittest.makeSuite(MultilingualTests))
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

