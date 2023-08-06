###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


""" 
A collection of adapter to provide better indexing support for
CMF derived types.

$Id: cmf_adapters.py 1492 2006-04-07 06:37:38Z ajung $
"""


from zope.interface import implements 
from textindexng.interfaces import IObjectWrapper

class IndexableObjectWrapperAdapter:
    """ support for CMFCore.CatalogTool.IndexableObjectWrapper """

    implements(IObjectWrapper)

    def __init__(self, context):
        self.context = context

    def getWrappedObject(self):
        """ return the wrapped object from an 
            CMFCore.CatalogTool.IndexableObjectWrapper instance.
        """

        return self.context.__dict__['_IndexableObjectWrapper__ob']
