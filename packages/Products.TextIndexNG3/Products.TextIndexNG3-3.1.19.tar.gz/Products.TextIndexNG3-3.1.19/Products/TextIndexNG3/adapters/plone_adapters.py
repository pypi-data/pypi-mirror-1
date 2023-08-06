###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


""" 
A collection of adapter to provide out-of-the-box indexing support
for Plone content-types.

$Id: plone_adapters.py 1862 2007-07-02 17:22:45Z ajung $
"""


from zope.interface import implements 
from textindexng.interfaces import IIndexableContent
from textindexng.content import IndexContentCollector as ICC
from textindexng.logger import LOG


class BaseAdapter:
    """ Base adapter implementing basic functionality """

    implements(IIndexableContent)

    def __init__(self, context):
        self.context = context
        self.encoding = context.portal_properties.site_properties.default_charset
        self.language = context.Language()

    def _c(self, text):
        if not isinstance(text, unicode):
            try: 
                return unicode(text, self.encoding)
            except UnicodeDecodeError:
                LOG('Content from %s could not be converted to unicode using the site encoding %s' % 
                    (self.context.absolute_url(1), self.encoding))
                raise
        else:
            return text

    def indexableContent(self, fields):
        raise NotImplementedError


class PloneTextAdapter(BaseAdapter):
    """ An adapter for all common Plone types providing 
        text-only content.
    """

    implements(IIndexableContent)

    def indexableContent(self, fields):

        icc = ICC()

        if 'Title' in fields:
            icc.addContent('Title', self._c(self.context.Title()), self.language)

        elif 'Description' in fields:
            icc.addContent('Description', self._c(self.context.Description()), self.language)

        elif 'SearchableText' in fields:
            icc.addContent('SearchableText', self._c(self.context.SearchableText()), self.language)

        return icc


class ATFileAdapter(BaseAdapter):
    """ An adapter for ATFile """

    implements(IIndexableContent)

    def indexableContent(self, fields):

        icc = ICC()

        if 'Title' in fields:
            icc.addContent('Title', self._c(self.context.Title()), self.language)

        elif 'Description' in fields:
            icc.addContent('Description', self._c(self.context.Description()), self.language)

        elif 'SearchableText' in fields:
            f = self.context.getFile()
            if not f: return

            mt = f.getContentType()
            if mt == 'text/plain':
                icc.addContent('SearchableText', self._c(self.context.SearchableText() + str(f)), self.language)
            else:
                icc.addBinary('SearchableText', str(f), mt)

        else:
            raise ValueError('Unhandled indexes: %s' % fields)

        return icc



from textindexng.interfaces import IObjectWrapper

class ExtensibleObjectWrapperAdapter:
    """ support for CMFPlone.CatalogTool.ExtensibleObjectWrapper """

    implements(IObjectWrapper)

    def __init__(self, context):
        self.context = context

    def getWrappedObject(self):
        try:
            return self.context._obj
        except AttributeError:
            return self.context._IndexableObjectWrapper__ob

