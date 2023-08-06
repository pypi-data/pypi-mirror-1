###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
WinWord converter

$Id: doc.py 1171 2005-05-23 14:31:41Z ajung $
"""

import os, sys

from textindexng.baseconverter import BaseConverter

try:
    from Globals import package_home
    wvConf_file = os.path.join(package_home(globals()), 'wvText.xml')
except ImportError:
    wvConf_file = os.path.join(os.path.dirname(__file__), 'wvText.xml')


class Converter(BaseConverter):

    content_type = ('application/msword','application/ms-word','application/vnd.ms-word')
    content_description = "Microsoft Word"
    depends_on = 'wvWare'

    def convert(self, doc, encoding, mimetype):
        """Convert WinWord document to raw text"""
        
        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            return self.execute('wvWare -c utf-8 --nographics -x "%s" "%s" 2> nul:' % (wvConf_file, tmp_name)), 'utf-8'
        else:
            return self.execute('wvWare -c utf-8 --nographics -x "%s" "%s" 2> /dev/null' % (wvConf_file, tmp_name)), 'utf-8'

DocConverter = Converter()
