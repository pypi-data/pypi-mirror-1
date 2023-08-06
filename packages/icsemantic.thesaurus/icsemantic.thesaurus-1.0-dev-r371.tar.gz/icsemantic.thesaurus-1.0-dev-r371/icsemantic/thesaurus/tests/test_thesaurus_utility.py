# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_thesaurus_utility.py 296 2008-06-18 17:50:17Z flarumbe $
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
from icsemantic.thesaurus.Thesaurus import thesaurus_utility

from Products.CMFCore.utils import getToolByName
from icsemantic.thesaurus.interfaces import IThesaurus
from icsemantic.thesaurus.Thesaurus import Thesaurus
from Products.PloneTestCase.setup import portal_name
from pyThesaurus.Concept import Concept
from zope.app.component.hooks import setSite

import base

class TestThesaurus(base.icSemanticTestCase):

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

    def afterSetUp(self):
        setSite(self.portal)
        if self.thesaurusIsInstalled():
            self.uninstallThesaurus()
        self.removeThesaurusUtility()

    def testInstallThesaurus(self):
        """
        After Thesaurus is installed, Thesaurus Utility should exist.
        """
        assert(not self.existsThesaurusUtility())
        self.installThesaurus()
        assert(self.thesaurusIsInstalled())
        assert(self.existsThesaurusUtility())

    def testUninstallThesaurus(self):
        """
        Thesaurus is uninstalled correctly.
        """
        self.installThesaurus()
        self.uninstallThesaurus()
        assert(not self.thesaurusIsInstalled())

    def testLoadThesaurus(self):
        """
        Thesaurus is loaded at the utility.
        """
        self.installThesaurus()
        ut = self.thesaurusUtility()
        ut.load("../pyThesaurus/pyThesaurus/tests/data/sample000.rdf", "en")
        self.assertPreferedTermsSample000(ut)

    def testLoadThesaurusAndUninstallThesaurus(self):
        """
        Thesaurus is preserved after Thesaurus uninstallation.
        """
        self.installThesaurus()
        ut = self.thesaurusUtility()
        ut.load("../pyThesaurus/pyThesaurus/tests/data/sample000.rdf", "en")
        self.uninstallThesaurus()
        self.assertPreferedTermsSample000(ut)

    def testAppendConcepts(self):
        self.installThesaurus()
        t = self.thesaurusUtility()
        c = Concept(et = ["fútbol@es", "balón pie@es", "soccer@en", "football@en", "football@fr"], rt=["mundial@es"])
        t.append_concept(c)
        t.append_term("mundial@es", rt=["fútbol@es"])
        
        equiv = t.get_equivalent('soccer@en', ['en'], exclude=True)
        self.assertEqual(equiv, ["football@en"])
        
        relat = t.get_related('soccer@en', ['en', 'es'])
        self.assertEqual(relat, ["mundial@es"])
        
        relat = t.get_related('fútbol@es', ['en', 'es'])
        self.assertEqual(relat, ["mundial@es"])

    def testUtilityWrapper(self):
        """Test that the utility wrapper is working"""
        self.installThesaurus()
        try:
            t = thesaurus_utility()
        except NameError:
            self.fail('Thesaurus utility does not exist after install.')
        terms = getattr(t, 'terms', None)
        self.failIf(terms is None, 'Thesaurus utility wrapper not working.')

    def assertPreferedTermsSample000(self, ut):
        """
        Utility has sample000 prefered terms.
        """
        self.assertEqual(ut.get_prefered('animals@en',  ['en']), ['animals@en'])
        self.assertEqual(ut.get_prefered('creatures@en',  ['en']), ['animals@en'])
        self.assertEqual(ut.get_prefered('fauna@en',  ['en']), ['animals@en'])
        self.assertEqual(ut.get_prefered('fauna@en',  ['fr']), [])

    def installThesaurus(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct("icsemantic.thesaurus")

    def uninstallThesaurus(self):
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(("icsemantic.thesaurus",))

    def thesaurusIsInstalled(self):
        qi = self.portal.portal_quickinstaller
        return qi.isProductInstalled("icsemantic.thesaurus")

    def existsThesaurusUtility(self):
        sm = self.portal.getSiteManager()
        return "utilities" in sm.context.objectIds() and "IThesaurus" in sm.context.utilities.objectIds()

    def thesaurusUtility(self):
        return thesaurus_utility()

    def removeThesaurusUtility(self):
        if self.existsThesaurusUtility():
            ut = self.thesaurusUtility()
            fo = ut.getParentNode()
            fo.manage_delObjects("IThesaurus")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestThesaurus))
    return suite
