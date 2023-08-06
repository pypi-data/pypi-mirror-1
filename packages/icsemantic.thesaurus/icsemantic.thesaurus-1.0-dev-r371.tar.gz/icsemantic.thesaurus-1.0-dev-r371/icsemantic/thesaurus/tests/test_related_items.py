# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_related_items.py 292 2008-06-17 17:57:20Z flarumbe $
#
# end: Platecom header
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from icsemantic.thesaurus.config import *

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.setup import portal_name
from icsemantic.thesaurus.interfaces import IThesaurus

from AccessControl.SecurityManagement import newSecurityManager

import base

class TestRelatedItems(base.icSemanticTestCase):

    def warning(self, err):
        import sys
        sys.stderr.write("\nWarning: %s\n" % err)

    def error(self, err):
        import sys
        sys.stderr.write("\nERROR: %s\n" % err)

    def assertEqualSets(self, a, b):
        a.sort()
        b.sort()
        self.assertEqual(a, b)

    def testRelatedItems(self):
        doc1 = self.addDocument("doc1", "A document with wetness keyword", ["wetness"])
        doc2 = self.addDocument("doc2", "A document with dryness keyword", ["dryness"])
        doc3 = self.addDocument("doc3", "A document with no keywords", [])
        assert not self.documentIsRelatedTo(doc1, doc1)
        assert self.documentIsRelatedTo(doc1, doc2)
        assert not self.documentIsRelatedTo(doc1, doc3)
        assert self.documentIsRelatedTo(doc2, doc1)
        assert not self.documentIsRelatedTo(doc2, doc2)
        assert not self.documentIsRelatedTo(doc2, doc3)
        assert not self.documentIsRelatedTo(doc3, doc1)
        assert not self.documentIsRelatedTo(doc3, doc2)
        assert not self.documentIsRelatedTo(doc3, doc3)

    def addDocument(self, document_id, document_title, keywords):
        self.folder[self.thisTestFolderName()].invokeFactory("Document", document_id)
        doc = getattr( self.folder[self.thisTestFolderName()], document_id)
        doc.setTitle(document_title)
        doc.setSubject(keywords)
        doc.reindexObject()
        return doc

    def documentIsRelatedTo(self, aDocument, otherDocument):
        return otherDocument in aDocument.computeRelatedItems()

    def afterSetUp(self):
        self.login()
        self.setRoles(['Manager', 'Member'])
        """if self.isInstalled("icsemantic.core"):
            self.uninstall("icsemantic.core")
        if self.isInstalled("icsemantic.thesaurus"):
            self.uninstall("icsemantic.thesaurus")
        if self.isInstalled("icsemantic.catalog"):
            self.uninstall("icsemantic.catalog")

        self.install("icsemantic.thesaurus")
        self.install("icsemantic.catalog")
        self.install("icsemantic.core")"""
        if not self.isInstalled("icsemantic.core"):
            self.install("icsemantic.core")
        if not self.isInstalled("icsemantic.thesaurus"):
            self.install("icsemantic.thesaurus")
        if not self.isInstalled("icsemantic.catalog"):
            self.install("icsemantic.catalog")

        self.loadThesaurus()
        self.prepareEmptyFolder(self.thisTestFolderName())

    def thisTestFolderName(self):
        return "icsemantic.core.relatedItems"

    def loadThesaurus(self):
        self.thesaurus_utility().load("src/pyThesaurus/pyThesaurus/tests/data/sample001.rdf", "en")

    def install(self, product_name):
        return self.qi().installProduct(product_name)

    def uninstall(self, product_name):
        return self.qi().uninstallProducts((product_name,))

    def isInstalled(self, product_name):
        return self.qi().isProductInstalled(product_name)

    def qi(self):
        return self.portal.portal_quickinstaller

    def prepareEmptyFolder(self, folder_name):
        if not folder_name in self.folder.objectIds():
            self.folder.invokeFactory('Folder', id=folder_name)
        for id in self.folder[folder_name].objectIds():
            self.folder[folder_name].manage_delObjects(id)

    def thesaurus_utility(self):
        sm = self.portal.getSiteManager()
        ut = sm.utilities.queryUtility(IThesaurus)
        if ut is None:
            raise NameError, "Thesaurus utility does not exist. Please, reinstall icsemantic.thesaurus product."
        return ut

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelatedItems))
    return suite
