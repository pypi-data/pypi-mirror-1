###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


"""
Component Vocabularies for the utility-adding view
of the Ting-Index.

Contributed by Frank Burkhardt

$Id: vocabulary.py 1570 2006-06-03 10:53:37Z ajung $
"""

from textindexng.interfaces import ISplitter, ILexicon, IStorage, IParser
from zope.app.component.vocabulary import UtilityVocabulary
from zope.app.schema.interfaces import IVocabularyFactory
from zope.interface import classProvides

class SplitterVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = ISplitter

class LexiconVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = ILexicon

class StorageVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = IStorage

class ParserVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = IParser

