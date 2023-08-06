# -*- coding: iso-8859-15 -*-

################################################################
# SRMedia
#
# (C) 2006 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

from Products.PloneTestCase import PloneTestCase

import os, sys
import tempfile, glob

PloneTestCase.installProduct('Five')
PloneTestCase.installProduct('CMFPlone')
PloneTestCase.installProduct('TextIndexNG3')

# setup a new Plohn site    
PloneTestCase.setupPloneSite(products=('TextIndexNG3', ))


class PloneTests(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        membership = self.portal.portal_membership
        membership.addMember('god', 'god', ('Manager',), ())

        self.login('god')
        self.portal.txng_convert_indexes()

    def testSetup(self):
        c = self.portal.portal_catalog
        indexes = c.Indexes
        self.assertEqual(indexes['SearchableText'].meta_type, 'TextIndexNG3')
        self.assertEqual(indexes['Title'].meta_type, 'TextIndexNG3')



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PloneTests))
    return suite

