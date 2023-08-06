# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: azaxview.py 262 2008-06-12 21:14:31Z flarumbe $
#
# end: Platecom header

try:
    from azax import AzaxBaseView, force_unicode
    from azax.plugins.core.interfaces import IKSSCoreCommands
    from azax.plugins.effects.interfaces import IScriptaculousEffectsCommands
except ImportError:
    try:
        from Products.azax import AzaxBaseView, force_unicode
        from Products.azax.plugins.core.interfaces import IKSSCoreCommands
        from Products.azax.plugins.effects.interfaces import IScriptaculousEffectsCommands
    except ImportError:
	from kss.core import force_unicode
        from kss.core.kssview import AzaxBaseView
        from kss.core.plugins.core.interfaces import IKSSCoreCommands
	from kss.core.plugins.effects.interfaces import IScriptaculousEffectsCommands

from Products.CMFPlone.utils import safe_unicode

from pyThesaurus.config import relations
from pyThesaurus.config import relation_name
from pyThesaurus.Concept import Concept
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.core.vocabularies import LanguagesVocabularyFactory
import icsemantic.core.browser.admin

import cgi

class AzaxView(AzaxBaseView):

    #header_macros = ViewPageTemplateFile('browser/header_macros.pt')

    def openConcept(self, cid, openedConcepts):
        if not cid in openedConcepts.split(","):
            self.setOpenedConcepts(openedConcepts)
            t = thesaurus_utility()
            int_cid = int(cid)
            concept = t[int_cid]
            term = self.preferedTerm(concept)
            self.insertHTMLConcept(id=cid, term=term, cid=int_cid, concept=concept)
            self.updateOpenedConcepts()
        return self.render()
    
    def addTerm(self, term, language, openedConcepts):
        self.setOpenedConcepts(openedConcepts)
        newterm = term + "@" + language
        if not newterm in self.openedTerms():
            self.insertHTMLConcept(id=newterm, term=newterm)
            self.updateOpenedConcepts()
        return self.render()

    def saveConcepts(self, conceptsRelations, openedConcepts):
        self.setOpenedConcepts(openedConcepts)
        self.emptyConceptsRelations(self.termsRelationsList(conceptsRelations))
        self.appendTermsToConceptsRelations(self.termsRelationsList(conceptsRelations))
        self.appendNewConcepts()
        self.replaceNewConceptsHTML()
        thesaurus_utility().commit()
        self.updateOpenedConcepts()
        #print conceptsRelations
        #IKSSCoreCommands(self).insertHTMLAsLastChild('div#dhtmlgoodies_mainContainer', "GRABAR: " + conceptsRelations)
        return self.render()
    
    def viewPage(self, pageRange, context, term, search, languages, format):
        self.setRequestIfNotEmpty('context', context)
        self.setRequestIfNotEmpty('term', term)
        self.setRequestIfNotEmpty('search', search)
        self.setRequestIfNotEmpty('languages', languages)
        self.setRequestIfNotEmpty('format', format)
        begin_index = int(pageRange.split(":")[0])
        end_index = int(pageRange.split(":")[1])
        IKSSCoreCommands(self).replaceInnerHTML('ul#allItems', self.query_result(begin_index, end_index))
        return self.render()
    
    def conceptsSearch(self, context, term, search, languages, format, elementsByPage, showall):
        self.setRequestIfNotEmpty('context', context)
        self.setRequestIfNotEmpty('term', term)
        self.setRequestIfNotEmpty('search', search)
        self.setRequestIfNotEmpty('languages', languages)
        self.setRequestIfNotEmpty('format', format)
        self.setRequestIfNotEmpty('elementsByPage', elementsByPage)
        self.setRequestIfNotEmpty('showall', showall)
        begin_index = self.paging_begin_index()
        end_index = self.paging_end_index()
        IKSSCoreCommands(self).replaceInnerHTML('ul#allItems', self.query_result(begin_index, end_index))
        IKSSCoreCommands(self).replaceHTML('input#currentSearchExpression', u'<input type="hidden" name="currentSearchExpression" id="currentSearchExpression" value="' + cgi.escape(search) + '">')
        IKSSCoreCommands(self).replaceInnerHTML('span#pagingHeader', self.paging_header())
        return self.render()

    def insertHTMLConcept(self, id, term, cid=None, concept=None):
        term_box = self.html_term_box(id, cid, concept, term)
        IKSSCoreCommands(self).insertHTMLAsLastChild('div#dhtmlgoodies_mainContainer', u'<div id="box_%s">%s</div>' % (safe_unicode(id), term_box))
        self.newOpenedConcept(id)

    def replaceHTMLConcept(self, newterm, cid):
        t = thesaurus_utility()
        id = repr(cid)
        concept = t[cid]
        term = self.preferedTerm(concept)
        term_box = self.html_term_box(id, cid, concept, term)

        IKSSCoreCommands(self).replaceHTML('div#box_%s' % safe_unicode(newterm), u'<div id="box_%s">%s</div>' % (safe_unicode(id), term_box))
        self.newOpenedConcept(id)
    
    def html_term_box(self, id, cid, concept, term):
        term_box = "<p align=\"center\">%s</p>" % safe_unicode(term)
        for r in relations:
            term_box += self.html_relation_div(id, r, cid, concept, term)
        return term_box
    
    def html_relation_div(self, id, r, cid, concept, term):
        relation_id = u"%s_%s" % (safe_unicode(id), cgi.escape(safe_unicode(r)))
        html_relation_div = u"<div>\n\t\t\t\t\t<p>" + cgi.escape(safe_unicode(relation_name[r])) + u":</p>"
        html_relation_div += u"\n\t\t\t\t\t<ul id=\"relation_" + relation_id + u"\">"
        html_relation_div += self.all_list_item(relation_id)
        if cid is not None:
            html_relation_div += self.related_terms(concept[r], cid, r)
        elif r == '=':
            html_relation_div += self.term_list_item(term, -1, r)
        html_relation_div += u"\n\t\t\t\t\t</ul>"
        html_relation_div += u"\n\t\t\t\t</div>"
        return html_relation_div

    def openedTerms(self):
        t = thesaurus_utility()
        terms = []
        for id in self.openedConcepts():
            if id.find('@') != -1:
                terms.append(id)
            elif id != 'x':
                terms.append(self.preferedTerm(t[int(id)]))
        return terms
    
    def setOpenedConcepts(self, openedConcepts):
        self._openedConcepts = openedConcepts
    
    def newOpenedConcept(self, id):
        self._openedConcepts += "," + id

    def openedConcepts(self):
        return self._openedConcepts.split(',')
    
    def updateOpenedConcepts(self):
        IKSSCoreCommands(self).replaceHTML('input#openedConcepts', u'<input type="hidden" id="openedConcepts" name="openedConcepts" value="' + cgi.escape(safe_unicode(self._openedConcepts)) + '">')
    
    def paging_begin_index(self):
        return self.thesaurusQuery().paging_begin_index()
    
    def paging_end_index(self):
        return self.thesaurusQuery().paging_end_index()

    def query_result(self, begin_index, end_index):
        html = ""
        if self.format() == "draganddrop":
            html = self.all_list_item()
        for (term, cid) in self.query_result_terms()[begin_index:end_index]:
            if self.format() == "simple":
                html += term + "<br>"
            else:
                html += self.term_list_item(term, cid)
        return html

    def query_result_concepts(self):
        if not hasattr(self, "_query_result_concepts"):
            if not self.has_parameter('context') and not self.has_parameter('term') and not self.has_parameter('search'):
                self._query_result_concepts = self.concepts()
            elif self.has_parameter('term'):
                self._query_result_concepts = self.term_concepts()
            elif self.has_parameter('search'):
                self._query_result_concepts = self.concepts_search()
            else:
                raise Exception, "Incorrect parameters."
        return self._query_result_concepts
    
    def query_result_terms(self):
        if not hasattr(self, "_query_result_terms"):
            t = thesaurus_utility()
            self._query_result_terms = [ (self.preferedTerm(t[cid]), cid) for cid in self.query_result_concepts() if len(t[cid].get_prefered(self.languages())) > 0 ]
        return self._query_result_terms

    def concepts(self):
        return thesaurus_utility().concepts()

    def term_concepts(self):
        return thesaurus_utility().term_concepts_ids(self.term_parameter(), self.context_parameter())

    def concepts_search(self):
        return thesaurus_utility().concepts_search_ids(self.search_parameter(), self.context_parameter())

    def languages(self):
        if self.has_parameter('languages'):
            return self.request['languages'].split(",")
        else:
            return [ language.value for language in LanguagesVocabularyFactory(self.context) ]
    
    def format(self):
        if self.has_parameter('format'):
            return self.request['format']
        else:
            return "draganddrop"
    
    def has_parameter(self, parameter):
        return self.request.has_key(parameter) and self.request[parameter] != ""

    def context_parameter(self):
        if self.has_parameter('context'):
            return self.request['context']
        else:
            return None

    def term_parameter(self):
        return self.request['term']

    def search_parameter(self):
        return self.request['search']
    
    def setRequestIfNotEmpty(self, parameter, value):
        if value != "":
            self.request.set(parameter, value)

    def appendTermsToConceptsRelations(self, termsRelations):
        """
        It appends terms of relations of expanded concepts that appear in the page.
        """
        for (concept, r, term) in termsRelations:
            concept[r].append(term)

    def emptyConceptsRelations(self, termsRelations):
        """
        It empties concepts expanded by the user relations.
        """
        for (concept, r, term) in termsRelations:
            for r in relations:
                concept[r] = list()
    
    def appendNewConcepts(self):
        """
        It appends valid new concepts created by user.
        """
        for term, concept in self.newConcepts().items():
            if term in concept['=']:
                cid = self.appendNewConcept(concept)
                self.newConcepts()[term] = cid # OJO: The concept is replaced by its cid

    def appendNewConcept(self, concept):
        return thesaurus_utility().append_concept(concept)

    def replaceNewConceptsHTML(self):
        """
        Now the new concepts are opened concept.
        """
        for term, cid in self.newConcepts().items():
            if type(cid) == type(1):
                self.replaceHTMLConcept(term, cid)
    
    def termsRelationsList(self, conceptsRelations):
        """
        Returns a list of (concept, relationSymbol, term) that appear expanded in the page.
        """
        ret = []
        for relationAndTerm in conceptsRelations.split(";"):
            if not relationAndTerm.startswith("allItems") and not relationAndTerm.startswith("selectedItems"):
                relation = relationAndTerm.split("|")[0]
                term = relationAndTerm.split("|")[1].split("_")[0]
                if term != "all":
                    id = relation.split("_")[1]
                    r = relation.split("_")[2]
                    ret.append((self.concept(id), r, term))
        return ret
    
    def concept(self, id):
        try:
            cid = int(id)
            aConcept = thesaurus_utility()[cid]
        except:
            aConcept = self.newConcept(id)
        return aConcept
    
    def newConcept(self, term):
        if not term in self.newConcepts():
            self.newConcepts()[term] = Concept(et=[term])
        return self.newConcepts()[term]
    
    def newConcepts(self):
        if not hasattr(self, "_newConcepts"):
            self._newConcepts = dict()
        return self._newConcepts
    
    def related_terms(self, terms, cid, r):
        html = ""
        for term in terms:
            html += self.term_list_item(term, cid, r)
        return html

    def all_list_item(self, box_id="results"):
        return u"\n\t\t\t\t\t\t<li id=\"all_" + box_id + u"\"><img src=\"fullscreenexpand_icon.gif\" border=\"0\" id=\"dragimage_all_" + box_id + u"\"> All</li>"

    def term_list_item(self, term, cid, r=""):
        id = u"%s_%d" % (cgi.escape(safe_unicode(term)), cid)
        if r != "":
            id += u"-copy%s" % cgi.escape(r)
        return u"\n\t\t\t\t\t\t<li id=\"" + id + u"\"><img src=\"search_icon.gif\" border=\"0\" id=\"expandimage_" + id + "\" class=\"open-concept\" kukit:cid=\"" + repr(safe_unicode(cid)) + u"\"><img src=\"fullscreenexpand_icon.gif\" border=\"0\" id=\"dragimage_" + id + u"\">" + cgi.escape(safe_unicode(term)) + u"</li>"

    def newterm_list_item(self, term):
        id = u"%s_%d-copy%d" % (safe_unicode(term), -1, self.newTermCopyId())
        return u"\n\t\t\t\t\t\t<li id=\"" + id + u"\"><img src=\"fullscreenexpand_icon.gif\" border=\"0\" id=\"dragimage_" + id + u"\">" + safe_unicode(term) + u"</li>"
    
    def newTermCopyId(self):
        if not hasattr(self, "_newTermCopyId"):
            _newTermCopyId = 0
        _newTermCopyId -= 1
        return _newTermCopyId
    
    def paging_header(self):
        return self.thesaurusQuery().paging_header()
    
    def thesaurusQuery(self):
        if not hasattr(self, "_thesaurusQuery"):
            self.setThesaurusQuery(icsemantic.thesaurus.browser.admin.ThesaurusQuery(self.context, self.request))
            self._thesaurusQuery.setAzaxview(self)
        return self._thesaurusQuery
    
    def setThesaurusQuery(self, thesaurusQuery):
        self._thesaurusQuery = thesaurusQuery

    def preferedTerm(self, concept):
        return concept.get_prefered(self.languages())[0]
