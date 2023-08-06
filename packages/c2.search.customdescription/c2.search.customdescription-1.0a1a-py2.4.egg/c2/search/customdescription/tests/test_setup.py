#!/usr/bin/env python
# encoding: utf-8
"""
test_setup.py

Created by Manabu Terada on 2009-11-11.
Copyright (c) 2009 CMScom. All rights reserved.
"""

from Products.CMFCore.utils import getToolByName

import c2.search.customdescription
import base

class TestInstall(base.ProductTestCase):
    """ Install basic test """ 
    def afterSetUp(self):
        pass

    def testQuickInstall(self):
        qi = self.portal.portal_quickinstaller
        self.failUnless('c2.search.customdescription' in (p['id'] for p in qi.listInstallableProducts()))
        qi.installProduct('c2.search.customdescription')
        self.failUnless(qi.isProductInstalled('c2.search.customdescription'))
    
class TestSkinInstall(base.ProductTestCase):
    """  """
    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('c2.search.customdescription')

    def testSkinLayersInstalled(self):
        self.skins = self.portal.portal_skins
        # print self.skins.objectIds()
        self.failUnless('c2customdescription' in self.skins.objectIds())
        self.assertEqual(len(self.skins.c2customdescription.objectIds()), 1)

class TestAddingCatalog(base.ProductTestCase):
    """ adding the catalog metadata""" 
    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('c2.search.customdescription')         
    
    def testMetadata(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        self.failUnless('SearchableText' in cat.schema())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    suite.addTest(makeSuite(TestSkinInstall))
    suite.addTest(makeSuite(TestAddingCatalog))
    return suite
