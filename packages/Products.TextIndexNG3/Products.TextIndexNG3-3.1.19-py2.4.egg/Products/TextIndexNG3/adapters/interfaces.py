###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface


class IATFile(Interface):
    """ marker interface for ATFile@CMFPlone """

class IPlainPlohnContent(Interface):
    """ marker interface for content types providing their
        indexable content as plain text through SearchableText(),
        Description() and Title()
    """
