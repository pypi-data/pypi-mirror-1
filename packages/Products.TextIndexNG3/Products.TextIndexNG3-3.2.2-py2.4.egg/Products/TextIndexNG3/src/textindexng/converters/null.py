###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
a stupid null converter

$Id: null.py 1909 2008-01-03 18:08:40Z ajung $
"""

from textindexng.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Plain text"

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        return doc, encoding

NullConverter = Converter()
