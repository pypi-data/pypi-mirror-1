# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: admin.py 262 2008-06-12 21:14:31Z flarumbe $
#
# end: Platecom header
"""
admin setting and preferences
Solo vistas y forms

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import os
from datetime import datetime

import zope
from zope import component
from zope.component import getUtility
from zope.formlib import form
from zope.app.form.browser import MultiSelectSetWidget
from zope.app.form.browser.itemswidgets import MultiSelectWidget \
        as BaseMultiSelectWidget, DropdownWidget, SelectWidget
from zope.app.form.browser import FileWidget

try:
    from zope.lifecycleevent import ObjectModifiedEvent
except:
    from zope.app.event.objectevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from icsemantic.core import pkg_home
from icsemantic.core.i18n import _
from icsemantic.core.vocabularies import LanguagesVocabularyFactory
from icsemantic.core.browser.base import BaseSettingsForm
from icsemantic.thesaurus import interfaces
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.thesaurus.browser.incrementalSearchSelectWidget import IncrementalSearchSelectWidgetFactory
from azaxview import AzaxView

class ThesaurusUpload( BaseSettingsForm ):
    """ Configlet for upload a thesaurus rdf file.
    """
    form_name = _(u'Thesaurus upload')
    form_fields = form.Fields( interfaces.IicSemanticManagementThesaurusUpload )
    form_fields['thesaurus_file'].custom_widget = FileWidget

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context,
                             self.form_fields,
                             data,
                             self.adapters):
            self.load_thesaurus(data['thesaurus_file'],
			    data['default_language'],
			    contexts=[data['thesaurus_context']],
			    format=data['thesaurus_format'],
			    encoding=data['encoding'],
			    new=data['new'])

            zope.event.notify(
                ObjectModifiedEvent(self.context)
                )
            self.status = _(
                "Updated on ${date_time}",
                mapping={'date_time': str(datetime.utcnow())}
                )
        else:
            self.status = _('No changes')

    def load_thesaurus(self, file_content, default_language,
		    contexts=[], format='SKOSCore', encoding='utf-8',
		    new=False):
        # TODO: add a field Language
        thesaurus_utility().load_string(file_content, default_language,
			contexts=contexts, format=format, encoding=encoding,
			new=new)

class ThesaurusDownload( BrowserView ):
    """ Download thesaurus and query concepts as an RDF File.
    """
    def rdf_string(self):
        return thesaurus_utility().rdf_string()

    def rdf_term_concepts(self):
        return thesaurus_utility().rdf_term_concepts(self.term_parameter(), self.context_parameter())

    def rdf_concepts_search(self):
        return thesaurus_utility().rdf_concepts_search(self.search_parameter(), self.context_parameter())

    def context_parameter(self):
        if self.request.has_key('context'):
            return self.request['context']
        else:
            return None

    def term_parameter(self):
        return self.request['term']

    def search_parameter(self):
        return self.request['search']

class ThesaurusQuery( BrowserView ):
    """ Query the thesaurus.
    """

    def query_result(self):
        return self.azaxview().query_result(self.paging_begin_index(), self.paging_end_index())
    
    def paging_header(self):
        atFirstPage = self.paging_begin_index() == 0
        atLastPage = self.paging_end_index() == len(self.query_result_terms())
        if atFirstPage and atLastPage:
            html = "All results"
        else:
            html = "Page: <select id=\"pageRange\" name=\"pageRange\">" + self.html_page_options() + "</select>"
        return html

    def newTermLanguage(self):
        return "<select id=\"newTermLanguage\" name=\"newTermLanguage\">" + self.html_newTermLanguage_options() + "</select>"
    
    def html_page_options(self):
        html = ""
        for page in range(1, self.last_page()+1):
            html += "<option value=\"%d:%d\"" % (self.paging_begin_index_of(page), self.paging_end_index_of(page))
            if page == self.page():
                html += " selected"
            html += ">%d</option>" % page
        return html
    
    def html_newTermLanguage_options(self):
        html = ""
        for language in LanguagesVocabularyFactory(self.context):
            html += "<option value=\"%s\"" % language.value
            if language.value == self.defaultLanguage():
                html += " selected"
            html += ">%s</option>" % language.title
        return html

    def defaultLanguage(self):
        # TODO: usar utility icsemantic.core.languages.PlatecomPreferredLanguage
        return "es"
    
    def paging_range_of(self, page):
        if self.listIsPaged():
            elementsbypage = self.elementsByPage()
            begin_index = (page - 1) * elementsbypage
            end_index = min(begin_index + elementsbypage, len(self.query_result_terms()))
        else:
            begin_index = 0
            end_index = len(self.query_result_terms())
        return (begin_index, end_index)

    def paging_range(self):
        return paging_range_of(self.page())

    def paging_begin_index(self):
        return self.paging_begin_index_of(self.page())
    
    def paging_end_index(self):
        return self.paging_end_index_of(self.page())

    def paging_begin_index_of(self, page):
        return self.paging_range_of(page)[0]
    
    def paging_end_index_of(self, page):
        return self.paging_range_of(page)[1]
    
    def last_page(self):
        if self.listIsPaged():
            page = (len(self.query_result_terms()) - 1) // self.elementsByPage() + 1
        else:
            page = 1
        return page

    def listIsPaged(self):
        return not self.has_parameter('showall')
    
    def elementsByPage(self):
        if self.has_parameter('elementsbypage'):
            return int(self.request['elementsbypage'])
        else:
            return 20
    
    def page(self):
        if self.has_parameter('page'):
            return int(self.request['page'])
        else:
            return 1

    def has_parameter(self, parameter):
        return self.request.has_key(parameter) and self.request[parameter] != ""
    
    def query_result_terms(self):
        return self.azaxview().query_result_terms()
    
    def azaxview(self):
        if not hasattr(self, "_azaxview"):
            self.setAzaxview(AzaxView(self.context, self.request))
        return self._azaxview
    
    def setAzaxview(self, azaxview):
        self._azaxview = azaxview


class VerticalSelectTest( BaseSettingsForm ):
    """ Test the incremental search select widget.
    """
    form_name = _(u'Vertical Select Test Form')
    form_fields = form.Fields( interfaces.IicSemanticVerticalSelectTest )
    form_fields['vertical_select'].custom_widget = IncrementalSearchSelectWidgetFactory

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context,
                             self.form_fields,
                             data,
                             self.adapters):
            zope.event.notify(
                ObjectModifiedEvent(self.context)
                )
            self.status = _(
                "Updated on ${date_time}.\nConcepts selected: ${selected_concepts}",
                mapping={
                    'date_time': str(datetime.utcnow()),
                    'selected_concepts': str(data['vertical_select'])
                }
                )
        else:
            self.status = _('No changes')
