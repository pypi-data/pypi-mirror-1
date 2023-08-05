###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class IObjectWrapper(Interface):
    """ interface for objects being wrapped by some kind of wrapper
        e.g. CMFCore.CatalogTool.IndexableObjectWrapper
    """

    def getWrappedObject():
        """ return the wrapped object """
