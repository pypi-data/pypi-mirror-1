# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_thesaurus_download.py 296 2008-06-18 17:50:17Z flarumbe $
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
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.thesaurus.browser.admin import ThesaurusDownload
from icsemantic.thesaurus.browser.admin import ThesaurusQuery

from zope.app.component.hooks import setSite

import base

class TestThesaurusDownload(base.icSemanticTestCase):


    def warning(self, err):
        import sys
        sys.stderr.write("\nWarning: %s\n" % err)

    def error(self, err):
        import sys
        sys.stderr.write("\nERROR: %s\n" % err)

    def testThesaurusDownloadRDF(self):
        rdf_downloaded = self.thesaurusDownload()
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#wetness@en\"><skos:prefLabel xml:lang=\"en\">wetness</skos:prefLabel><skos:altLabel xml:lang=\"en\">dryness</skos:altLabel></skos:Concept><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#shrubs@en\"><skos:prefLabel xml:lang=\"en\">shrubs</skos:prefLabel><skos:altLabel xml:lang=\"en\">bushes</skos:altLabel></skos:Concept><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#rocks@en\"><skos:prefLabel xml:lang=\"en\">rocks</skos:prefLabel><skos:altLabel xml:lang=\"en\">basalt</skos:altLabel><skos:altLabel xml:lang=\"en\">granite</skos:altLabel><skos:altLabel xml:lang=\"en\">slate</skos:altLabel></skos:Concept></rdf:RDF>"
        assert rdf_downloaded == rdf_expected
    
    def testReadConceptsRDF(self):
        rdf_downloaded = self.readTermConcepts("bushes@en")
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#shrubs@en\"><skos:prefLabel xml:lang=\"en\">shrubs</skos:prefLabel><skos:altLabel xml:lang=\"en\">bushes</skos:altLabel></skos:Concept></rdf:RDF>"
        assert rdf_downloaded == rdf_expected
    
    def testSearchConceptsRDF(self):
        rdf_downloaded = self.searchConcepts("wet")
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#wetness@en\"><skos:prefLabel xml:lang=\"en\">wetness</skos:prefLabel><skos:altLabel xml:lang=\"en\">dryness</skos:altLabel></skos:Concept></rdf:RDF>"
        #self._where_are_different(rdf_downloaded, rdf_expected)
        #return
        assert rdf_downloaded == rdf_expected

        rdf_downloaded = self.searchConcepts("dry")
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#wetness@en\"><skos:prefLabel xml:lang=\"en\">wetness</skos:prefLabel><skos:altLabel xml:lang=\"en\">dryness</skos:altLabel></skos:Concept></rdf:RDF>"
        assert rdf_downloaded == rdf_expected

        rdf_downloaded = self.searchConcepts("bas.lt")
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#rocks@en\"><skos:prefLabel xml:lang=\"en\">rocks</skos:prefLabel><skos:altLabel xml:lang=\"en\">basalt</skos:altLabel><skos:altLabel xml:lang=\"en\">granite</skos:altLabel><skos:altLabel xml:lang=\"en\">slate</skos:altLabel></skos:Concept></rdf:RDF>"
        assert rdf_downloaded == rdf_expected

        rdf_downloaded = self.searchConcepts("s")
        rdf_expected = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<rdf:RDF xmlns:xml=\"http://www.w3.org/XML/1998/namespace\" xmlns:foaf=\"http://xmlns.com/foaf/0.1/\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dcterms=\"http://purl.org/dc/terms/\" xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\"><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#shrubs@en\"><skos:prefLabel xml:lang=\"en\">shrubs</skos:prefLabel><skos:altLabel xml:lang=\"en\">bushes</skos:altLabel></skos:Concept><skos:Concept rdf:about=\"http://platecom.inter-cultura.com/concepts#rocks@en\"><skos:prefLabel xml:lang=\"en\">rocks</skos:prefLabel><skos:altLabel xml:lang=\"en\">basalt</skos:altLabel><skos:altLabel xml:lang=\"en\">granite</skos:altLabel><skos:altLabel xml:lang=\"en\">slate</skos:altLabel></skos:Concept></rdf:RDF>"
        assert rdf_downloaded == rdf_expected

    def testThesaurusDownloadHTML(self):
        html_downloaded = self.thesaurusConceptsListHTML()
        html_expected = "wetness@en<br>shrubs@en<br>rocks@en<br>"
        assert html_downloaded == html_expected
    
    def testReadConceptsHTML(self):
        html_downloaded = self.readTermConceptsHTML("bushes@en")
        html_expected = "shrubs@en<br>"
        assert html_downloaded == html_expected

    def testSearchConceptsHTML(self):        
        html_downloaded = self.searchConceptsHTML("wet")
        html_expected = "wetness@en<br>"
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsHTML("dry")
        html_expected = "wetness@en<br>"
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsHTML("bas.lt")
        html_expected = "rocks@en<br>"
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsHTML("s")
        html_expected = "shrubs@en<br>rocks@en<br>"
        assert html_downloaded == html_expected
    
    def testReadConceptsHTMLBis(self):
        self.loadThesaurus("../pyThesaurus/pyThesaurus/tests/data/open_thesaurus_es.txt", language="es", format="Ding")

        html_downloaded = self.searchConceptsHTML("#", ["es"])
        html_expected = ""
        assert html_downloaded == html_expected

    def thesaurusDownload(self):
        browserView = ThesaurusDownload(self.portal, self.app.REQUEST)
        return browserView.rdf_string()

    def readTermConcepts(self, term):
        self.app.REQUEST.set('term', term)
        browserView = ThesaurusDownload(self.portal, self.app.REQUEST)
        return browserView.rdf_term_concepts()

    def searchConcepts(self, search_expression):
        self.app.REQUEST.set('search', search_expression)
        browserView = ThesaurusDownload(self.portal, self.app.REQUEST)
        return browserView.rdf_concepts_search()

    def thesaurusConceptsListHTML(self, languages=["en"], page="", elementsbypage=""):
        browserView = ThesaurusQuery(self.portal, self.app.REQUEST)
        self.app.REQUEST.set('languages', ",".join(languages))
        self.app.REQUEST.set('format', 'simple')
        if elementsbypage != '' or page != '':
            self.app.REQUEST.set('page', page)
            self.app.REQUEST.set('elementsbypage', elementsbypage)
        else:
            self.app.REQUEST.set('showall', 'true')
        return browserView.query_result()

    def readTermConceptsHTML(self, term, languages=["en"], page="", elementsbypage=""):
        self.app.REQUEST.set('term', term)
        self.app.REQUEST.set('languages', ",".join(languages))
        self.app.REQUEST.set('format', 'simple')
        if elementsbypage != '' or page != '':
            self.app.REQUEST.set('page', page)
            self.app.REQUEST.set('elementsbypage', elementsbypage)
        else:
            self.app.REQUEST.set('showall', 'true')
        browserView = ThesaurusQuery(self.portal, self.app.REQUEST)
        return browserView.query_result()

    def searchConceptsHTML(self, search_expression, languages=["en"], page="", elementsbypage=""):
        self.app.REQUEST.set('search', search_expression)
        self.app.REQUEST.set('languages', ",".join(languages))
        self.app.REQUEST.set('format', 'simple')
        if elementsbypage != '' or page != '':
            self.app.REQUEST.set('page', page)
            self.app.REQUEST.set('elementsbypage', elementsbypage)
        else:
            self.app.REQUEST.set('showall', 'true')
        browserView = ThesaurusQuery(self.portal, self.app.REQUEST)
        return browserView.query_result()

    def afterSetUp(self):
        setSite(self.portal)
        self.login()
        self.setRoles(['Manager', 'Member'])
        self.portal.portal_languages.addSupportedLanguage("es")
        self.loadThesaurus("../pyThesaurus/pyThesaurus/tests/data/sample001.rdf")

    def loadThesaurus(self, filename, language="en", format='SKOSCore', encoding='latin1'):
        self.thesaurus_utility().clean()
        self.thesaurus_utility().load(filename, language, format=format, encoding=encoding)

    def thesaurus_utility(self):
        return thesaurus_utility()
    
    def _where_are_different(self, aString, anotherString):
        if aString == anotherString:
            print "Both strings are equal."
        else:
            print "String 1:"
            print aString
            print "String 2:"
            print anotherString
            print "length 1: %d" % len(aString)
            print "length 2: %d" % len(anotherString)
            for i in range(min(len(aString), len(anotherString))):
                if aString[i] != anotherString[i]:
                    print "first difference at: %d" % i
                    print "character 1: '%c'" % aString[i]
                    print "character 2: '%c'" % anotherString[i]
                    break

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestThesaurusDownload))
    return suite
