# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_thesaurus_download.py 261 2008-06-12 21:09:24Z flarumbe $
#
# end: Platecom header
import unittest
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.thesaurus.browser.admin import ThesaurusQuery
from icsemantic.thesaurus.browser.azaxview import AzaxView
from zope.app.component.hooks import setSite

import base

class TestThesaurusAdmin(base.icSemanticTestCase):

    def testSaveConceptsRelations(self):
        conceptsRelations = u"allItems|all_results;allItems|abarraganamiento@es_61;allItems|abarraganarse@es_62;allItems|adulterio@es_418;allItems|adúltero@es_426;allItems|aguacharse@es_531;allItems|ajuntarse@es_605;allItems|amanerado@es_828;allItems|amanerado@es_829;allItems|amanerar@es_830;allItems|amanerar@es_831;allItems|amansar@es_832;allItems|amansar@es_833;allItems|amante@es_834;allItems|amante@es_835;allItems|amanuense@es_836;allItems|barraganería@es_1670;allItems|engolamiento@es_3163;allItems|madrugada@es_6142;allItems|madrugar@es_6143;allItems|melindre@es_6265;selectedItems|all_selected;relation_nuevotermino@es_=|all_nuevotermino@es_=;relation_nuevotermino@es_=|nuevotermino@es_-1-copy=;relation_nuevotermino@es_=|engolamiento@es_3163-copy1;relation_nuevotermino@es_-|all_nuevotermino@es_-;relation_nuevotermino@es_-|barraganería@es_1670-copy2;relation_nuevotermino@es_#|all_nuevotermino@es_#;relation_nuevotermino@es_#|madrugada@es_6142-copy3;relation_nuevotermino@es_<|all_nuevotermino@es_<;relation_nuevotermino@es_>|all_nuevotermino@es_>;relation_nuevotermino@es_!|all_nuevotermino@es_!;relation_nuevotermino@es_~|all_nuevotermino@es_~"
        self.saveConcepts(conceptsRelations)

        table = [
                    ("nuevotermino@es", '=', ["nuevotermino@es", "engolamiento@es"]),
                    ("nuevotermino@es", '-', [u"barraganería@es"]),
                    ("nuevotermino@es", '#', ["madrugada@es"]),
                    ("nuevotermino@es", '<', []),
                    ("nuevotermino@es", '>', []),
                    ("nuevotermino@es", '!', []),
                    ("nuevotermino@es", '~', [])
                ]
        self.conceptsRelationsCorrect(conceptsRelations, table)
    
    def testReadConceptsHTMLBis(self):
        html_downloaded = self.readTermConceptsHTML("ababa@es", ["es"])
        html_expected = "ababa@es<br>ababol@es<br>"
        assert html_downloaded == html_expected
    
    def testReadConceptsHTMLBis(self):
        html_downloaded = self.searchConceptsHTML("#", ["es"])
        html_expected = ""
        assert html_downloaded == html_expected
    
    def testConceptsPagingAll(self):
        html_downloaded = self.searchConceptsHTML("ama", ["es"])
        html_expected = u"ababa@es<br>ababol@es<br>abarraganamiento@es<br>abarraganarse@es<br>acaramelado@es<br>acerbo@es<br>acongojar@es<br>adiestrador@es<br>adorable@es<br>adorar@es<br>adulterio@es<br>adúltero@es<br>afectivo@es<br>aferrar@es<br>aficionado@es<br>agonía@es<br>agrado@es<br>agraz@es<br>agriar@es<br>aguacharse@es<br>aguar@es<br>ajuntarse@es<br>ama@es<br>ama@es<br>amaestrado@es<br>amagar@es<br>amago@es<br>amainar@es<br>amalgama@es<br>amalgamar@es<br>amalgamar@es<br>amanerado@es<br>amanerado@es<br>amanerar@es<br>amanerar@es<br>amansar@es<br>amansar@es<br>amante@es<br>amante@es<br>amanuense@es<br>amar@es<br>amarar@es<br>amargar@es<br>amarillear@es<br>amarras@es<br>amarre@es<br>amarre@es<br>amarrete@es<br>amartillar@es<br>amartillar@es<br>amasar@es<br>amasar@es<br>amazacotado@es<br>amañarse@es<br>amaño@es<br>amigable@es<br>amortiguar@es<br>anclaje@es<br>apañado@es<br>apelmazar@es<br>atado@es<br>atentamente@es<br>barloa@es<br>barraganería@es<br>batiburrillo@es<br>benigno@es<br>bilioso@es<br>bilis@es<br>bita@es<br>bácara@es<br>cabalgador@es<br>cabildear@es<br>dársena@es<br>engolamiento@es<br>erróneo@es<br>erótico@es<br>falso@es<br>foguear@es<br>gentil@es<br>gentileza@es<br>grato@es<br>gualdo@es<br>lactancia@es<br>lactar@es<br>liar@es<br>ligar@es<br>madama@es<br>madrugada@es<br>madrugar@es<br>masaje@es<br>mazacote@es<br>melindre@es<br>molesto@es<br>nana@es<br>nobleza@es<br>quemazón@es<br>valido@es<br>yacer@es<br>zabila@es<br>ámbar@es<br>"
        assert html_downloaded == html_expected
        
    def testAllConceptsPagingPage1(self):
        html_downloaded = self.thesaurusConceptsListHTML(languages=["es"], page="1", elementsbypage="20")
        html_expected = u"Biblia@es<br>Dios@es<br>Jesucristo@es<br>Pelota@es<br>UCI@es<br>Yahvé@es<br>a priori@es<br>a propósito@es<br>a quemarropa@es<br>a ultranza@es<br>ababa@es<br>ababol@es<br>ababol@es<br>abacera@es<br>abacero@es<br>abacería@es<br>abacial@es<br>abacora@es<br>abacorar@es<br>abacá@es<br>"
        assert html_downloaded == html_expected

    def testConceptsPagingPage1(self):
        html_downloaded = self.searchConceptsHTML("ama", ["es"], page="1", elementsbypage="10")
        html_expected = u"ababa@es<br>ababol@es<br>abarraganamiento@es<br>abarraganarse@es<br>acaramelado@es<br>acerbo@es<br>acongojar@es<br>adiestrador@es<br>adorable@es<br>adorar@es<br>"
        assert html_downloaded == html_expected
    
    def testConceptsPagingPage2(self):
        html_downloaded = self.searchConceptsHTML("ama", ["es"], page="2", elementsbypage="10")
        html_expected = u"adulterio@es<br>adúltero@es<br>afectivo@es<br>aferrar@es<br>aficionado@es<br>agonía@es<br>agrado@es<br>agraz@es<br>agriar@es<br>aguacharse@es<br>"
        assert html_downloaded == html_expected
    
    def testConceptsPagingPage10(self):
        html_downloaded = self.searchConceptsHTML("ama", ["es"], page="10", elementsbypage="10")
        html_expected = u"mazacote@es<br>melindre@es<br>molesto@es<br>nana@es<br>nobleza@es<br>quemazón@es<br>valido@es<br>yacer@es<br>zabila@es<br>ámbar@es<br>"
        assert html_downloaded == html_expected
    
    def testPageList(self):
        html_downloaded = self.searchConceptsPageList("aman", ["es"], page="1", elementsbypage="10")
        html_expected = u'Page: <select id="pageRange" name="pageRange"><option value="0:10" selected>1</option><option value="10:20">2</option><option value="20:21">3</option></select>'
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsPageList("aman", ["es"], page="2", elementsbypage="10")
        html_expected = u'Page: <select id="pageRange" name="pageRange"><option value="0:10">1</option><option value="10:20" selected>2</option><option value="20:21">3</option></select>'
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsPageList("aman", ["es"], page="3", elementsbypage="10")
        html_expected = u'Page: <select id="pageRange" name="pageRange"><option value="0:10">1</option><option value="10:20">2</option><option value="20:21" selected>3</option></select>'
        assert html_downloaded == html_expected

        html_downloaded = self.searchConceptsPageList("aman", ["es"], page="1", elementsbypage="100")
        html_expected = u'Todos los resultados'
        assert html_downloaded == html_expected

    def testOpenConcept(self):
        html_downloaded = self.openConcept(cid="22")

    def testViewPage(self):
        html_downloaded = self.viewPage("1:10", search="aman", languages="es")
    
    def testSearchRequest(self):
        html_downloaded = self.searchRequest(search="ama", languages="es")
    
    def testAddTerm(self):
        html_downloaded = self.addTerm(term="unTermino", language="es")
        html_downloaded = self.addTerm(term="unTermino", language="es", openedConcepts="x,210,unTermino@es")
        html_downloaded = self.addTerm(term="acatarrarse", language="es", openedConcepts="x,210,unTermino@es")
    
    def testSaveNewConcept(self):
        conceptsRelations = "allItems|all_results;allItems|wetness@en_0;allItems|shrubs@en_1;allItems|rocks@en_2;selectedItems|all_selected;relation_2_=|all_2_=;relation_2_=|rocks@en_2-copy=;relation_2_=|slate@en_2-copy=;relation_2_-|all_2_-;relation_2_-|granite@en_2-copy=;relation_2_-|basalt@en_2-copy=;relation_2_#|all_2_#;relation_2_<|all_2_<;relation_2_>|all_2_>;relation_2_!|all_2_!;relation_2_~|all_2_~;relation_unTermino@es_=|all_unTermino@es_=;relation_unTermino@es_=|unTermino@es_unTermino@es_=;relation_unTermino@es_=|otroTermino@es_unTermino@es_="
        html_downloaded = self.saveConcepts(conceptsRelations)

    def openConcept(self, cid, openedConcepts="x"):
        return self.azaxview().openConcept(cid, openedConcepts)

    def viewPage(self, pageRange, context="", term="", search="", languages="", format=""):
        return self.azaxview().viewPage(pageRange, context, term, search, languages, format)

    def searchRequest(self, context="", term="", search="", languages="", format="", elementsByPage="", showall=""):
        return self.azaxview().conceptsSearch(context, term, search, languages, format, elementsByPage, showall)

    def addTerm(self, term, language, openedConcepts="x"):
        return self.azaxview().addTerm(term, language, openedConcepts)

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

    def searchConceptsPageList(self, search_expression, languages=["en"], page="", elementsbypage=""):
        self.app.REQUEST.set('search', search_expression)
        self.app.REQUEST.set('languages', ",".join(languages))
        self.app.REQUEST.set('format', 'simple')
        if elementsbypage != '' or page != '':
            self.app.REQUEST.set('page', page)
            self.app.REQUEST.set('elementsbypage', elementsbypage)
        else:
            self.app.REQUEST.set('showall', 'true')
        browserView = ThesaurusQuery(self.portal, self.app.REQUEST)
        return browserView.paging_header()
    
    def saveConcepts(self, conceptsRelations, openedConcepts="x"):
        return self.azaxview().saveConcepts(conceptsRelations, openedConcepts)

    def conceptsRelationsCorrect(self, conceptsRelations, table):
        t = self.thesaurus_utility()
        for (term, relation, relatedTerms) in table:
            cid = t(term)[0]
            self.assertEqual(t[cid][relation], relatedTerms)

    def afterSetUp(self):
        setSite(self.portal)
        self.login()
        self.setRoles(['Manager', 'Member'])
        self.portal.portal_languages.addSupportedLanguage("es")
        self.loadThesaurus("../pyThesaurus/pyThesaurus/tests/data/open_thesaurus_es.txt", language="es", format="Ding")
    
    def azaxview(self):
        return AzaxView(self.portal, self.app.REQUEST)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestThesaurusAdmin))
    return suite
