###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


from logger import LOG 

def handle_exc(text, obj, exc_info):
    """ Handle an exception. Currently we log the exception through  our own
        logger. 'obj' is currently unused. We might use it later to obtain
        detailed informations.
    """
    print text
    LOG.error(text, exc_info=exc_info)


