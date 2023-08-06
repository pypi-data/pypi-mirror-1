#!/usr/bin/env python

###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from distutils.core import setup,Extension

import sys

setup(name = "TextIndexNGExtensions",
      version = "3.0.5",
      author = "Andreas Jung",
      author_email = "andreas@andreas-jung.com",
      description = "Helper modules for TextIndexNG3: Splitter, stemmers, normalizer and support ",
      url = "http://sf.net/projects/textindexng/",
      namespace_packages=['zopyx'],
      py_modules=['zopyx.__init__', 'zopyx.txng3.__init__'],

          ext_modules=[

            Extension("zopyx.txng3.normalizer",
                [ "zopyx/txng3/normalizer/normalizer.c" ],
            ),

            Extension("zopyx.txng3.splitter",
                [ "zopyx/txng3/splitter/splitter.c",
                  "zopyx/txng3/splitter/hashtable.c",
                  "zopyx/txng3/splitter/dict.c" 
                ],
            ),

            Extension("zopyx.txng3.support",
                [ "zopyx/txng3/support.c" ],
            ),

            Extension("zopyx.txng3.stemmer",
                ["zopyx/txng3/stemmer/stemmer.c" ,
                 "zopyx/txng3/stemmer/libstemmer_c/libstemmer/libstemmer.c",
                 "zopyx/txng3/stemmer/libstemmer_c/runtime/api.c",
                 "zopyx/txng3/stemmer/libstemmer_c/runtime/utilities.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_danish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_dutch.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_english.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_finnish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_french.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_german.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_italian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_norwegian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_porter.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_portuguese.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_spanish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_ISO_8859_1_swedish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_KOI8_R_russian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_danish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_dutch.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_english.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_finnish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_french.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_german.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_italian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_norwegian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_porter.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_portuguese.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_russian.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_spanish.c",
                 "zopyx/txng3/stemmer/libstemmer_c/src_c/stem_UTF_8_swedish.c",
                ],
                include_dirs=['zopyx/txng3/stemmer/libstemmer_c/include', 
                              'zopyx/txng3/stemmer/libstemmer_c',
                              'zopyx/txng3/stemmer/libstemmer_c/libstemmer'],
            ),
        ]
    )


if sys.platform != "win32":
    ext_args = ['-Wall']
else:
    ext_args = []

extLevensthein = Extension('zopyx.txng3.levenshtein',
                           sources = ['zopyx/txng3/python-Levenshtein-0.10/Levenshtein.c'],
                           extra_compile_args=ext_args)

setup (name = 'python-Levenshtein',
       version = '0.10',
       description = 'Python extension computing string distances and similarities.',
       author = 'David Necas (Yeti)',
       author_email = 'yeti@physics.muni.cz',
       license = 'GNU GPL',
       url = 'http://trific.ath.cx/python/levenshtein/',
       long_description = '''
Levenshtein computes Levenshtein distances, similarity ratios, generalized
medians and set medians of Strings and Unicodes.  Because it's implemented
in C, it's much faster than corresponding Python library functions and
methods.
''',
       ext_modules = [extLevensthein])

