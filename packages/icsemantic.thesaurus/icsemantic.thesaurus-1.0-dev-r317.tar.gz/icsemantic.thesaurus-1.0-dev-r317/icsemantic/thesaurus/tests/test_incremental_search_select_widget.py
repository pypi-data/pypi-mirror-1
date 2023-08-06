# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_thesaurus_download.py 261 2008-06-12 21:09:24Z flarumbe $
#
# end: Platecom header
import unittest
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.thesaurus.browser.admin import VerticalSelectTest
from icsemantic.thesaurus.browser.incrementalSearchSelectWidget import IncrementalSearchSelectAzax
from zope.app.component.hooks import setSite

import base

class TestIncrementalSearchSelectWidget(base.icSemanticTestCase):

    def testChooseSelectedConcept(self):
        print self.chooseSelectedConcept("formverticalSelect", "amar@es, antoja")

    def testAutocompleteConcepts(self):
        print self.autocompleteConcepts("formverticalSelect", "amar, temer")

    def testVerticalSelect(self):
        #print self.openVerticalSelectTestPage()
        pass

    def openVerticalSelectTestPage(self):
        vertical_select = VerticalSelectTest(self.portal, self.app.REQUEST)()

    def autocompleteConcepts(self, widgetName, searchExpression):
        return self.incrementalSearchSelectAzax().autocompleteConcepts(widgetName, searchExpression)

    def chooseSelectedConcept(self, widgetName, searchExpression):
        return self.incrementalSearchSelectAzax().chooseSelectedConcept(widgetName, searchExpression)

    def incrementalSearchSelectAzax(self):
        return IncrementalSearchSelectAzax(self.portal, self.app.REQUEST)

    def afterSetUp(self):
        setSite(self.portal)
        self.login()
        self.setRoles(['Manager', 'Member'])
        self.portal.portal_languages.addSupportedLanguage("es")
        self.loadThesaurus("../pyThesaurus/pyThesaurus/tests/data/open_thesaurus_es.txt", language="es", format="Ding")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIncrementalSearchSelectWidget))
    return suite
