###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
a stupid null converter

$Id: null.py 1072 2005-05-01 12:05:51Z ajung $
"""

from textindexng.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Null converter"

    def convert(self, doc, encoding, mimetype):
        return doc, encoding

NullConverter = Converter()
