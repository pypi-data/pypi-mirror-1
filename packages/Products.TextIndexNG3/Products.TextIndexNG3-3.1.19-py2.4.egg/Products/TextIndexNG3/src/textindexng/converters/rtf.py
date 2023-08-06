###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
a simple RTF converter

$Id: rtf.py 1456 2006-02-08 14:10:27Z ajung $
"""

import xml.sax
import cStringIO
from xml.sax.handler import ContentHandler

from textindexng.baseconverter import BaseConverter


class RTFtextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("UTF-8") + ' ')

    def startDocument(self):
        self._data = cStringIO.StringIO()

    def getData(self):
        return self._data.getvalue()


class Converter(BaseConverter):

    content_type = ('application/rtf','text/rtf')
    content_description = "RTF"
    depends_on = 'rtf2xml'

    def convert(self, doc, encoding, mimetype):
        """ convert RTF Document """
        handler = RTFtextHandler()
        tmp_name = self.saveFile(doc)
        xmlstr = self.execute('cd /tmp && rtf2xml --no-dtd "%s"' % tmp_name)
        xml.sax.parseString(xmlstr, handler)
        return handler.getData(), 'utf-8'

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'utf-8'

RTFConverter = Converter()
