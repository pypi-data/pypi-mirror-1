###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import re

from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy

from textindexng.interfaces import ISplitter
from zopyx.txng3.splitter import Splitter as _Splitter


class Splitter:
    """ A wrapper for TXNGSplitter """

    implements(ISplitter)

    def __init__(self, *args, **kw):
        self._splitter = _Splitter(**kw)

    def split(self, content):
        return self._splitter.split(content)


class SplitterFactory:
    
    implements(IFactory)

    def __call__(self, maxlen=64, singlechar=True, casefolding=True, separator='+'):
        splitter = Splitter(maxlen=maxlen, singlechar=singlechar, casefolding=casefolding, separator=separator)
        return splitter

    def getInterfaces(self):
        return implementedBy(Splitter)

SplitterFactory = SplitterFactory()


# patterns used by the splitter (will be compiled to regexes)
SPLIT_AT = '\s|\t'
PUNCTUATION = '\.|,|\?|\!|:|;'

class SimpleSplitter:
    """ A simple unicode-aware splitter """

    implements(ISplitter)

    def __init__(self, casefolding=1, split_at=SPLIT_AT, punctuation=PUNCTUATION, *args, **kw):
        """ 'split_at' -- a regular expression that is used to split strings.
            The regular expression is passed unchanged to re.compile().
        """
        self.splitter = re.compile(split_at, re.I | re.M | re.UNICODE)
        self.punctuation = re.compile(punctuation+"$", re.I | re.M | re.UNICODE)
        self.casefolding = casefolding

    def split(self, content):
        """ Split a text string (prefered unicode into terms according to the
            splitter regular expression.
        """
        split = self.splitter.split
        punctuation = self.punctuation.sub
        if self.casefolding:
            content = content.lower()
        terms = [punctuation('', t.strip()) for t in split(content)]
        terms = [t for t in terms if t]
        return terms


class SimpleSplitterFactory:
    
    implements(IFactory)

    def __call__(self, split_at=SPLIT_AT, punctuation=PUNCTUATION, *args, **kw):
        return SimpleSplitter(split_at=split_at, punctuation=punctuation)

    def getInterfaces(self):
        return implementedBy(SimpleSplitter)

SimpleSplitterFactory = SimpleSplitterFactory()
