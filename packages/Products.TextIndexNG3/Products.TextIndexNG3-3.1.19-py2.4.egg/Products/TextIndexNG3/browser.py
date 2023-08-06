###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from Globals import InitializeClass

from Products.Five import BrowserView

class IndexView(BrowserView):

    def test_index(self, query, parser, encoding='iso-8859-15'):
        """ perform a query and return the search result as list of
            object paths
        """
        rs = self.context.index.search(unicode(query, encoding), parser=parser)
        return [self.context.getpath(docid) for docid in rs.getDocids()]

    def words_vocabulary(self, pattern, language='en'):
        """ return all words from the lexicon that match a particualar
            pattern for a given language.
        """
        words = self.context.index.getLexicon().getWordsForPattern(pattern, language)
        words.sort()
        return words

    def _getUtilitiesFor(self, iface):
        """ return everything registered for an interface """
        from zope.app import zapi
        return zapi.getUtilitiesFor(iface)

    def get_converters(self):
        """ return all available converters """
        from textindexng.interfaces import IConverter
        return self._getUtilitiesFor(IConverter)

    def get_storages(self):
        """ return all available storages """
        from textindexng.interfaces import IStorage
        return self._getUtilitiesFor(IStorage)

    def get_lexicons(self):
        """ return all available lexicons """
        from textindexng.interfaces import ILexicon
        return self._getUtilitiesFor(ILexicon)

    def get_thesauruses(self):
        """ return all available thesaurus"""
        from textindexng.interfaces import IThesaurus
        return self._getUtilitiesFor(IThesaurus)

    def get_thesaurus(self):
        """ return the content for a particular thesurus """
        from zope.app import zapi
        from textindexng.interfaces import IThesaurus
        return zapi.getUtility(IThesaurus, self.request['id'])

    def get_splitters(self):
        """ return all available lexicons """
        from textindexng.interfaces import ISplitter
        return self._getUtilitiesFor(ISplitter)

    def get_parsers(self):
        """ return all available lexicons """
        from textindexng.interfaces import IParser
        return self._getUtilitiesFor(IParser)

    def documents_for_word(self):
        """ return all document paths for a given word """
        word = self.request['word']
        wid = self.context.index.getLexicon().getWordId(word)
        docids = self.context.index.getStorage(self.context.index.fields[0]).getDocumentsForWordId(wid)
        return [self.context.getpath(docid) for docid in docids]


    def get_adapters(self):
        """ return all registered adapters"""

        from textindexng.interfaces import IIndexableContent

        try:
            # zope 2.10
            from zope.component.globalregistry import getGlobalSiteManager as getSiteManager
        except ImportError:
            # zope 2.9
            try:
                from zope.app.zapi import getSiteManager
            except ImportError:
                raise RuntimeError('This functionality is only available in Zope 2.9 or higher')

        try:
            # zope 2.10
            from zope.component.registry import AdapterRegistration
        except:
            # Zope 2.9
            from zope.component.site import AdapterRegistration

        lst = []

        try:
            # zope 2.10
            registrations = getSiteManager().registeredAdapters()
        except:
            # Zope 2.9
            registrations = getSiteManager().registrations()

        for reg in registrations:
            if reg.provided == IIndexableContent:

                try:
                    # Zope 2.10
                    yield (reg.required, reg.factory)
                except:
                    # Zope 2.9
                    yield (reg.required, reg.value)

InitializeClass(IndexView)
