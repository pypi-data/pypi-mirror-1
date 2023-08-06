###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
TextIndexNG test case

$Id: TextIndexNGTestCase.py 1811 2007-02-27 20:58:58Z ajung $
"""

import unittest

from zope.component.interfaces import IFactory
from zope.app.testing import placelesssetup, ztapi

from textindexng.splitter import SplitterFactory, SimpleSplitterFactory
from textindexng.normalization import Normalizer
from textindexng.stopwords import Stopwords
from textindexng.lexicon import LexiconFactory
from textindexng.storage import StorageFactory
from textindexng.converters.pdf import PDFConverter
from textindexng.parsers.english import EnglishParser
from textindexng.interfaces import IConverter, IStopwords, INormalizer, IParser


class TextIndexNGTestCase(unittest.TestCase):
    """ base test case class for indexer related tests """

    def setUp(self):
        placelesssetup.setUp()
        ztapi.provideUtility(IConverter, PDFConverter, 'application/pdf')
        ztapi.provideUtility(IFactory, SplitterFactory , 'txng.splitters.default')
        ztapi.provideUtility(IFactory, SimpleSplitterFactory , 'txng.splitters.simple')
        ztapi.provideUtility(IParser, EnglishParser(), 'txng.parsers.en')
        ztapi.provideUtility(IFactory, LexiconFactory, 'txng.lexicons.default')
        ztapi.provideUtility(IFactory, StorageFactory, 'txng.storages.default')
        ztapi.provideUtility(IStopwords, Stopwords())
        ztapi.provideUtility(INormalizer, Normalizer())

    def tearDown(self):
        placelesssetup.tearDown()
