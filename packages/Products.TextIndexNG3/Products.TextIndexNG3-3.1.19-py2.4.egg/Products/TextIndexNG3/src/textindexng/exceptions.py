###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Exception used throughout TextIndexNG

$Id: exceptions.py 1548 2006-06-03 10:49:34Z ajung $
"""

class BaseConverterError(Exception): pass
class LexiconError(Exception): pass
class NormalizerError(Exception): pass
class StopwordError(Exception): pass
class StorageException(Exception): pass
