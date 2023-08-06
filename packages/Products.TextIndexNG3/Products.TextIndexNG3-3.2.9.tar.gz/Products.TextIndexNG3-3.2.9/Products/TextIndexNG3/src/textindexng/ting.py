###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

# This code has been contribued by Ivo van der Wijk
# This code was improved by Frank Burkhardt
# More improvements and tests by Simon Pamies

import zope.interface

from zope.index import interfaces
from zope.app import zapi

import zope.app.container.contained
import zope.app.catalog.attribute
import zope.app.catalog.interfaces

from textindexng.index import Index

import persistent
import re

from textindexng.interfaces.ting import ITingIndex

from textindexng import config
from textindexng.interfaces import IStorageWithTermFrequency

class TingIndex(zope.app.catalog.text.TextIndex, 
                persistent.Persistent):

    zope.interface.implements(
        interfaces.IInjection,
        interfaces.IStatistics,
        interfaces.IIndexSearch,
        ITingIndex
        )

    def __init__(self, field_name=None, interface=None, field_callable=False,
     use_stemmer=config.defaults['use_stemmer'],
     dedicated_storage=config.defaults['dedicated_storage'],
     ranking=config.defaults['ranking'],
     use_normalizer=config.defaults['use_normalizer'],
     languages=config.DEFAULT_LANGUAGE,
     use_stopwords=config.defaults['use_stopwords'],
     autoexpand_limit=config.defaults['autoexpand_limit'],
     splitter=config.DEFAULT_SPLITTER,
     index_unknown_languages=config.defaults['index_unknown_languages'],
     query_parser=config.DEFAULT_PARSER,
     lexicon=config.DEFAULT_LEXICON,
     splitter_additional_chars=config.defaults['splitter_additional_chars'],
     storage=config.DEFAULT_STORAGE,
     splitter_casefolding=config.defaults['splitter_casefolding']):
        spaces=re.compile(r'\s+')
        if ranking:
            util=zapi.createObject(storage)
            if not IStorageWithTermFrequency.providedBy(util):
                raise ValueError("This storage cannot be used for ranking")
        _fields=spaces.split(field_name)
        zope.app.catalog.attribute.AttributeIndex.__init__(self,_fields[0],interface,field_callable)
        if len(_fields) < 2:
            dedicated_storage=False
        _default_fields=[_fields[0]]
        self._index = Index(
            fields=_fields,
            languages=spaces.split(languages),
            use_stemmer=use_stemmer,
            dedicated_storage=dedicated_storage,
            ranking=ranking,
            use_normalizer=use_normalizer,
            use_stopwords=use_stopwords,
            storage=storage,
            autoexpand_limit=autoexpand_limit,
            splitter=splitter,
            lexicon=lexicon,
            index_unknown_languages=index_unknown_languages,
            query_parser=query_parser,
            splitter_additional_chars=splitter_additional_chars,
            splitter_casefolding=splitter_casefolding
        )
        self.languages=languages
        self.use_stemmer=use_stemmer
        self.dedicated_storage=dedicated_storage
        self.ranking=ranking
        self.use_normalizer=use_normalizer
        self.use_stopwords=use_stopwords
        self.interface = interface
        self.storage=storage
        self.autoexpand_limit=autoexpand_limit
        self.default_fields=' '.join(_default_fields)
        self._fields=_fields
        self.splitter=splitter
        self.lexicon=lexicon
        self.index_unknown_languages=index_unknown_languages
        self.query_parser=query_parser
        self.splitter_additional_chars=splitter_additional_chars
        self.splitter_casefolding=splitter_casefolding

    def clear(self):
        self._index.clear()

    def documentCount(self):
        """See interface IStatistics"""
        return len(self._index.getStorage(self.default_fields[0]))

    def wordCount(self):
        """See interface IStatistics"""
        return len(self._index.getLexicon())

    def index_doc(self, docid, value):
        """See interface IInjection"""
        v = self.interface(value, None)
        if v is not None:
            self._index.index_object(v, docid)

    def unindex_doc(self, docid):
        """See interface IInjection"""
        self._index.unindex_object(docid)

    def apply(self, query):

        if isinstance(query,dict):
            kw=query
            query=kw['query']
            del kw['query']
        else:
            kw={}
            
        ting_rr = self._index.search(query,**kw)
        
        # never use keys because we want 
        # this list to be lazy
        return ting_rr.getDocids()

