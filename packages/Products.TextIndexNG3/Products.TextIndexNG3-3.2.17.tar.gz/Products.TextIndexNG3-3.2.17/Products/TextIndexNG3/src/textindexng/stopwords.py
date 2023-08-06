###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Stopwords

$Id: stopwords.py 1905 2007-12-29 12:47:33Z ajung $
"""

import os, re

from textindexng.interfaces import IStopwords
from zopyx.txng3.support import stopwordfilter
from zope.interface import implements

sw_dir = os.path.join(os.path.dirname(__file__), 'data', 'stopwords')

class Stopwords:
    """  class for handling stopwords """

    implements(IStopwords)

    def __init__(self):
        self._cache = {}

    def stopwordsForLanguage(self, language):
        if not self._cache.has_key(language):
            self._cache[language] = readStopwords(language)
        return self._cache[language].keys()

    def process(self, words, language): 
        cache = self._cache
        if not cache.has_key(language):
            cache[language] = readStopwords(language)
        return stopwordfilter(words, cache[language])

    def availableLanguages(self):
        files = [f for f in os.listdir(sw_dir) if f.endswith('.txt')]
        return [os.path.splitext(f)[0] for f in files]
        
    def __repr__(self):
        return self.__class__.__name__ 


enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')

def readStopwords(language):
    """ read a stopword file from the filesystem """
    
    words = {}    # words -> None 
    encoding = None

    fname = os.path.join(sw_dir, '%s.txt' % language) 
    if not os.path.exists(fname):
        return {}

    for l in open(fname): 
        if not l.strip(): continue

        mo = enc_reg.match(l)
        if mo:
            encoding= mo.group(1)
            continue

        if l.startswith('#'): continue

        word = unicode(l.strip(), encoding).lower()
        words[word] = None

    return words

StopwordUtility = Stopwords()

