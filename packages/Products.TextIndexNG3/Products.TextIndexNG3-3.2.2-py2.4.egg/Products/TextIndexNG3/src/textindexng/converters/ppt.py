###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
PowerPoint converter

$Id: ppt.py 1909 2008-01-03 18:08:40Z ajung $
"""

import sys
from textindexng.exceptions import ConversionError
from textindexng.baseconverter import BaseConverter
from textindexng.baseconverter import TmpFile
from textindexng.logger import LOG
from stripogram import html2text


class Converter(BaseConverter):

    content_type = ('application/mspowerpoint', 'application/ms-powerpoint', 
                'application/vnd.ms-powerpoint')
    content_description = "Microsoft PowerPoint"
    depends_on = 'ppthtml'

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        """Convert PowerPoint document to raw text"""
        
        tmp_name = self.saveFile(doc)
        err = TmpFile('')
        if sys.platform == 'win32':
            html = self.execute('ppthtml "%s" 2> "%s"' % (
                tmp_name, str(err)))
        else:
            html = self.execute('ppthtml "%s" 2> "%s"' % (
                tmp_name, str(err)))
        
        try:
            errors = open(str(err), 'r+').read()
        except OSError:
            errors = ""
        if errors:
            if logError:
                LOG.warn('Converter %s experienced an error %s' % (
                    self.content_description, errors)
                )
            
            if raiseException:
                raise ConversionError(errors)

        return html2text(html,
                         ignore_tags=('img',),
                         indent_width=4,
                         page_width=80), 'iso-8859-15'

PPTConverter = Converter()
