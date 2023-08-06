###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Content extraction

$Id: content.py 1610 2006-06-08 05:47:55Z ajung $
"""

import warnings

from zope.app import zapi
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError

from textindexng.interfaces import IConverter
from textindexng.interfaces import IIndexContentCollector, IIndexableContent, IObjectWrapper
from config import DEFAULT_LANGUAGE
from compatible import callable
from logger import LOG


class IndexContentCollector:

    implements(IIndexContentCollector)

    def __init__(self):
        self._d = {}

    def addContent(self, field, text, language=None):
        if not isinstance(text, unicode):
            raise ValueError("Argument for 'text' must be of type unicode (got: %s)" % type(text))
    
        self._d[field]={'content' : text,
                        'language' : language
                       }

    def addBinary(self, field, data, mimetype, encoding=None, language=None):
        self._d[field] = {'data' : data,
                          'encoding' : encoding,
                          'mimetype' : mimetype,
                          'language' : language
                         }

    def getFields(self):
        return self._d.keys()

    def getFieldData(self, field):
        return self._d[field]

    def setFieldData(self, field, d):
        self._d[field] = d

    def delFieldData(self, field):
        del self._d[field]

    def __nonzero__(self):
        return len(self._d) > 0 


def extract_content(fields, obj, default_language=DEFAULT_LANGUAGE):   
    """ This helper methods tries to extract indexable content from a content 
        object in different ways. First we try to check for ITextIndexable
        interface or ITextIndexableRaw interfaces which are the preferred 
        way to interace with TextIndexNG indexes. Otherwise we fall back
        to the standard Zope 2 behaviour and try to get the content by
        looking at the corresponding attributes or methods directly.
        Please note that this method will not contain content-type
        specific extraction code. This should be handled in every case by
        the content-type implementation itself or through an adapter.
    """

    # check if the object is an object wrapper then unwrap it first
    adapter = IObjectWrapper(obj, None)
    if adapter:
        obj = adapter.getWrappedObject()


    adapter = IIndexableContent(obj, None)
    if adapter:
        # the official TXNG3 indexer API

        icc = adapter.indexableContent(fields)

    elif hasattr(obj, 'txng_get'):

        # old Zope behaviour for objects providing the txng_get() hook
        warnings.warn('Using the txng_get() hook for class %s is deprecated.'
                      ' Use IndexContentCollector implementation instead' % obj.__class__.__name__, 
                       DeprecationWarning, 
                       stacklevel=2)
          
        result = obj.txng_get(fields)
        if result is None:
            return None

        # unpack result triple
        source, mimetype, encoding = result
        icc = IndexContentCollector()
        icc.addBinary(fields[0], source, mimetype, encoding, default_language)

    else:

        # old Zope 2 behaviour: look up value either as attribute of the object
        # or as method providing a return value as indexable content

        d = {}

        icc = IndexContentCollector()

        for f in fields:
            
            v = getattr(obj, f, None)
            if not v: continue
            if callable(v):
                v = v()

            # accept only a string/unicode string    
            if not isinstance(v, basestring):
                raise TypeError('Value returned for field "%s" must be string or unicode (got: %s, %s)' % (f, repr(v), type(v)))

            if isinstance(v, str):
                encoding = 'iso-8859-15'  # ATT: fix this
                v = unicode(v, encoding, 'ignore')
        
            icc.addContent(f, v, default_language)


    # now perform conversion through external converters if necessary

    if not icc:
        return None

    for f in icc.getFields():

        d = icc.getFieldData(f)
    
        # check if we need to convert
        if d.has_key('mimetype'):

            # We got some binary content from the object. So we should
            # lookup a converter registered as named utility 
            try:
                converter = zapi.getUtility(IConverter, d['mimetype'])
            except ComponentLookupError:
                LOG.warn('No converter registered for %s' % d['mimetype'])
                icc.delFieldData(f)
                continue

            converted_text, encoding = converter.convert(d['data'],    
                                                         d['encoding'],
                                                         d['mimetype'])

            # The result should be string/unicode. If not, convert the returned 
            # content to unicode using the returned encoding. The converter is
            # in charge to handle encoding issues correctly.

            assert isinstance(converted_text, basestring)
            if isinstance(converted_text, str):
                converted_text = unicode(converted_text, encoding, 'ignore')

            language = d['language'] or default_language

            # now replace the old field (containing content to be converted)
            icc.delFieldData(f)

            # with the converted content (as unicode)
            icc.addContent(f, converted_text, language)

    return icc
