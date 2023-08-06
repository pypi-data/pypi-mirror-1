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

$Id: plone_adapters.py 1828 2007-03-18 17:11:35Z ajung $
"""

from zope.component import adapts
from zope.interface import implements

from Products.ATContentTypes.interface.file import IATFile

from Products.TextIndexNG3.interfaces.wrapper import IExtensibleIndexableObjectWrapper
from textindexng.interfaces import IObjectWrapper
from cmf_adapters import CMFContentAdapter


class ATFileAdapter(CMFContentAdapter):

    """An adapter for ATCT files.
    """

    adapts(IATFile)

    def addSearchableTextField(self, icc):
        text = self._c(self.context.SearchableText())
        icc.addContent('SearchableText', text, self.language)

        f = self.context.getFile()
        if not f:
            return

        body = str(f)
        if body:
            mt = f.getContentType()
            if mt == 'text/plain':
                icc.addContent('SearchableText', self._c(body), self.language)
            else:
                icc.addBinary('SearchableText', body, mt, None, self.language)


class ExtensibleObjectWrapperAdapter:
    """ support for CMFPlone.CatalogTool.ExtensibleObjectWrapper """

    adapts(IExtensibleIndexableObjectWrapper)
    implements(IObjectWrapper)

    def __init__(self, context):
        self.context = context

    def getWrappedObject(self):
        return self.context._IndexableObjectWrapper__ob
