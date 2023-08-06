###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Excel Converter

$Id: xls.py 1072 2005-05-01 12:05:51Z ajung $
"""

import sys
from textindexng.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/msexcel','application/ms-excel','application/vnd.ms-excel')
    content_description = "Microsoft Excel"
    depends_on = 'xls2csv'

    def convert(self, doc, encoding, mimetype):
        """Convert Excel document to raw text"""

        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            return self.execute('xls2csv -d 8859-1 -q 0 "%s" 2> nul:' % tmp_name), 'iso-8859-15'
        else:
            return self.execute('xls2csv -d 8859-1 -q 0 "%s" 2> /dev/null' % tmp_name), 'iso-8859-15'

XLSConverter = Converter()
