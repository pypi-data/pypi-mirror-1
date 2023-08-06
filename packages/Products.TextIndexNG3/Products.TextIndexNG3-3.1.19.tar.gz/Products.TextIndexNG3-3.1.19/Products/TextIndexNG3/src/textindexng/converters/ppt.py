###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
PowerPoint converter

$Id: ppt.py 1331 2005-09-23 07:21:47Z ajung $
"""

import sys
from textindexng.baseconverter import BaseConverter
from stripogram import html2text


class Converter(BaseConverter):

    content_type = ('application/mspowerpoint', 'application/ms-powerpoint', 
                'application/vnd.ms-powerpoint')
    content_description = "Microsoft PowerPoint"
    depends_on = 'ppthtml'

    def convert(self, doc, encoding, mimetype):
        """Convert PowerPoint document to raw text"""
        
        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            html = self.execute('ppthtml "%s" 2> nul:' % tmp_name)
        else:
            html = self.execute('ppthtml "%s" 2> /dev/null' % tmp_name)

        return html2text(html,
                         ignore_tags=('img',),
                         indent_width=4,
                         page_width=80), 'iso-8859-15'

PPTConverter = Converter()
