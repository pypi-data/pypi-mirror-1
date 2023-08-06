
# ZopeTestCase was not designed to run tests as part of the
# Zope test suite proper. In particular, it intercepts product
# installation. We have to work around this for the Five tests
# by starting up Zope2 before doing anything else.
#
# Note: fivetest must be imported first thing by test modules!

def _part_of_zope_suite():
    # Find out if we run from softwarehome
    from os.path import normcase, realpath
    from App.config import getConfiguration
    softwarehome = normcase(realpath(getConfiguration().softwarehome))
    return normcase(realpath(__file__)).startswith(softwarehome)

def _start_zope():
    # Startup Zope 2.7 or 2.8+
    import Testing
    try:
        import Zope2 as Zope
    except ImportError:
        import Zope
    Zope.startup()

def _main():
    if _part_of_zope_suite():
        _start_zope()
    else:
        from Testing.ZopeTestCase import installProduct
        installProduct('Five')
        installProduct('ZCatalog')
        installProduct('TextIndexNG3')

_main()


from Testing.ZopeTestCase import *

class TextIndexNG3TestCase(ZopeTestCase):
    pass

