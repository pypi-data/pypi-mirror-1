from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from zope.app.component.hooks import getSite
import cgi

try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

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
        from kss.core.kssview import KSSView
        from kss.core.plugins.core.interfaces import IKSSCoreCommands
        from kss.core.plugins.effects.interfaces import IScriptaculousEffectsCommands

if not HAS_PLONE3:
    KSSView = AzaxBaseView

class IncrementalSearchSelectWidget(SimpleInputWidget):

    template = ViewPageTemplateFile('templates/incrementalSearchSelect-widget.pt')

    def __init__(self, context, request, thesaurus_context="", thesaurus_languages=[]):
        super(IncrementalSearchSelectWidget, self).__init__(context, request)
        self.extra = " autocomplete='off' concepts='' selectedIndex='' onfocus='timerIncrementalSearchSelect(this.id);' onkeypress='return keypressed(this.id, event)' size='50'"
        self._thesaurus_context = thesaurus_context
        self._thesaurus_languages = thesaurus_languages

    def __call__(self):
        html = self.template()
        html += super(IncrementalSearchSelectWidget, self).__call__()
        html += '<input type="hidden" name="%s_autocompletedExpression" id="%s_autocompletedExpression" value="" concepts="" selectedIndex="">' % (safe_name(self.name), safe_name(self.name))
        html += '<input type="hidden" name="%s_concepts" id="%s_concepts" value="">' % (safe_name(self.name), safe_name(self.name))
        html += '<input type="hidden" name="%s_selectedIndex" id="%s_selectedIndex" value="">' % (safe_name(self.name), safe_name(self.name))
        html += '<input type="hidden" name="%s_autocompleteConceptsAction" id="%s_autocompleteConceptsAction" class="incrementalSearchSelect" widgetName="%s" value="" concepts="">' % (self.name, self.name, self.name)
        html += '<input type="hidden" name="%s_chooseSelectedConceptAction" id="%s_chooseSelectedConceptAction" class="chooseSelectedConcept" widgetName="%s" value="" concepts="">' % (self.name, self.name, self.name)
        html += '<div id="div_%s"></div>' % safe_name(self.name) #TODO: replace to query
        return html
    
    def getInputValue(self):
        return self.selectedConcepts()
    
    def selectedConcepts(self):
        return [ int(strcid) for strcid in self.request["%s_concepts" % safe_name(self.name)].split(",") ]

class IncrementalSearchSelectAzax(KSSView):

    def autocompleteConcepts(self, widgetname, searchexpression, concepts, selectedindex):
        self.set_widgetName(widgetname)
        self.set_searchExpression(safe_unicode(searchexpression))
        self.set_concepts(safe_unicode(concepts))
        self.set_selectedIndex(selectedindex)
        self.detect_modifying_concept()
        self.html_showConceptsList()
        self.html_setSelectedIndex(str(self.selectedIndex()))
        return self.render()
    
    def detect_modifying_concept(self):
        terms = self.searchExpressionTerms()
        pref = self.selectedPreferedTerms()
        self.set_modifyingConcept(len(terms) - 1)
        for i in range(min(len(terms), len(pref))):
            if terms[i] != safe_unicode(pref[i]):
                self.set_modifyingConcept(i)
                break
    
    def html_showConceptsList(self):
        IKSSCoreCommands(self).replaceInnerHTML('div#div_%s' % self.safeWidgetName(), self.html_someConceptsList())

    def html_setSelectedIndex(self, aString):
        IKSSCoreCommands(self).setAttribute('input#%s_selectedIndex' % self.safeWidgetName(), "value", aString)

    def chooseSelectedConcept(self, widgetname, searchexpression, concepts, selectedindex):
        self.set_widgetName(widgetname)
        self.set_searchExpression(safe_unicode(searchexpression))
        self.set_concepts(safe_unicode(concepts))
        self.set_selectedIndex(selectedindex)
        self.detect_modifying_concept()
        (newSearchExpression, selectedConcept) = self.html_conceptSelectedSearchExpression()
        self.html_updateAutocompletedExpression(newSearchExpression)
        if selectedConcept != "" or self.allow_new_terms():
            self.updateSelectedConcept(selectedConcept)
            self.html_updateSelectedConcepts()
            self.html_hideConceptsList()
            self.html_setSelectedIndex("")
        return self.render()
    
    def updateSelectedConcept(self, selectedConcept):
        if self.modifyingConcept() > len(self.cids()) - 1:
            self.appendConcept(selectedConcept)
        else:
            self.updateConcept(self.modifyingConcept(), selectedConcept)

    def html_updateAutocompletedExpression(self, newSearchExpression):
        IKSSCoreCommands(self).setAttribute('input#%s_autocompletedExpression' % self.safeWidgetName(), "value", newSearchExpression)

    def html_hideConceptsList(self):
        IKSSCoreCommands(self).replaceInnerHTML('div#div_%s' % self.safeWidgetName(), "")

    def html_updateSelectedConcepts(self):
        IKSSCoreCommands(self).setAttribute('input#%s_autocompletedExpression' % self.safeWidgetName(), "concepts", self.concepts())

    def html_conceptSelectedSearchExpression(self):
        search_words = self.searchExpressionTerms()
        current_input = self.currentInput()
        if current_input == "":
            newSearchExpression = self.searchExpression()
            selectedConcept = ""
        else:
            results = self.query(current_input)
            if results['concepts_count'] > 0:
                selected_word = results['concepts'][self.selectedSubindex()][0]
                selectedConcept = results['concepts'][self.selectedSubindex()][1]
                search_words[self.modifyingConcept()] = selected_word
                newSearchExpression = (u", ").join(search_words)
                if self.modifyingConcept() == len(search_words) - 1:
                    newSearchExpression += (u", ")
            elif self.allow_new_terms(): #ACA SE CAMBIARAN LAS CONDICIONES
                if self.modifyingConcept() == len(search_words) - 1:
                    newSearchExpression = self.searchExpression() + (u", ")
                else:
                    newSearchExpression = self.searchExpression()
                selectedConcept = current_input
            else:
                newSearchExpression = self.searchExpression()
                selectedConcept = ""
        return (safe_unicode(newSearchExpression), selectedConcept)

    def html_someConceptsList(self):
        search_words = self.searchExpressionTerms()
        current_input = self.currentInput()
        html = ""
        if current_input != "":
            results = self.query(current_input)
            self.correct_selectedIndex(results['concepts_count'])
            if results['concepts_count'] > 0:
                selected_word = results['concepts'][self.selectedSubindex()][0]
            else:
                selected_word = ""

            html += "<table cellspacing='0' cellpadding='0' border='0'>"
            html += "    <tr>"
            html += "        <td><div id='searchResults' class='incrementalSearchSelectResults'>"
            for (term, cid) in results['concepts']:
                html += self.html_word_item(term, selected_word, current_input)
            if results['concepts_count'] > self.max_results():
                html += "            ...<br>"
            html += "            </div></td>"
            html += "        <td height='100%'>"
            if results['concepts_count'] > self.max_results():
                html += "<table cellspacing='0' cellpadding='0' border='0' height='100%'>"
                html += "                <tr><td style='vertical-align: top'><img src='arrowUp.gif' border='0' onclick='javascript:increment_selectedIndex(\"" + self.widgetName() + "\", -1);'></td></tr>"
                html += "                <tr><td style='vertical-align: bottom'><img src='arrowDown.gif' border='0' onclick='javascript:increment_selectedIndex(\"" + self.widgetName() + "\", +1);'></td></tr>"
                html += "            </table>"
            else:
                html += "&nbsp;"
            html += "</td>"
            html += "    </tr>"
            html += "</table>"
        return html

    def html_word_item(self, word, selected_word, current_input):
        if word == selected_word:
            return u"            <i>%s</i><br>" % self.html_emphasize_input(word, current_input)
        else:
            return u"            %s<br>" % self.html_emphasize_input(word, current_input)

    def html_emphasize_input(self, word, current_input):
        if current_input != "":
            return safe_unicode((u"<b>" + current_input + u"</b>").join(word.split(current_input)))
        else:
            return safe_unicode(word)
    
    def query(self, search_expression):
        return thesaurus_utility().query(search_expression=search_expression,
                                            narrowerthan = None,
                                            broaderthan = None,
                                            contexts = [],
                                            languages = supportedLanguages(),
                                            inbranch = None,
                                            hidden = None,
                                            max_results = self.max_results(),
                                            first_result = self.first_result())

    def first_result(self):
        return self.selectedIndex() - self.selectedSubindex()

    def selectedSubindex(self):
        return self.selectedIndex() % self.max_results()
    
    def max_results(self):
        return 5
    
    def allow_new_terms(self):
        return True

    def selectedIndex(self):
        return self._selectedIndex

    def set_selectedIndex(self, index):
        if index == "":
            self._selectedIndex = 0
        else:
            self._selectedIndex = int(index)

    def widgetName(self):
        return self._widgetName

    def set_widgetName(self, widgetName):
        self._widgetName = widgetName
    
    def safeWidgetName(self):
        return safe_name(self.widgetName())

    def correct_selectedIndex(self, concepts_count):
        self._selectedIndex = thesaurus_utility().correct_index(self._selectedIndex, concepts_count)

    def searchExpression(self):
        return self._searchExpression

    def set_searchExpression(self, aString):
        self._searchExpression = aString

    def concepts(self):
        return u",".join([ self.to_string(cid) for cid in self.cids() ])

    def set_concepts(self, aString):
        if aString == "":
            self.set_cids([])
        else:
            self.set_cids([self.to_int(str_cid) for str_cid in aString.split(",")])
    
    def appendConcept(self, cid):
        self.cids().append(cid)
    
    def updateConcept(self, index, cid):
        self.cids()[index] = cid
    
    def to_int(self, aString):
        try:
            aNumber = int(aString)
        except:
            aNumber = aString
        return aNumber
    
    def to_string(self, var):
        try:
            aString = str(var)
        except:
            aString = var
        return aString

    def cids(self):
        return self._cids

    def set_cids(self, aList):
        self._cids = aList

    def modifyingConcept(self):
        return self._modifyingConcept

    def set_modifyingConcept(self, aNumber):
        self._modifyingConcept = aNumber
    
    def searchExpressionTerms(self):
        return lstrip(self.searchExpression().split(","))
    
    def currentInput(self):
        return self.searchExpressionTerms()[self.modifyingConcept()]

    def selectedPreferedTerms(self):
        pref = []
        for cid in self.cids():
            try:
                pref.append(self.preferedTerm(int(cid)))
            except ValueError:
                pref.append(cid)
        return pref
    
    def preferedTerm(self, cid):
        return thesaurus_utility()[cid].get_prefered(supportedLanguages())[0]

def IncrementalSearchSelectWidgetFactory(context, request, thesaurus_context="", thesaurus_languages=[]):
    return IncrementalSearchSelectWidget(context, request, thesaurus_context, thesaurus_languages)

def safe_name(aString):
    return aString.replace(".", "")
        
def lstrip(words):
    return [ safe_unicode(word.lstrip()) for word in words ]
    
def preferredLanguage():
    return portal_languages().getPreferredLanguage()

def supportedLanguages():
    return portal_languages().getSupportedLanguages()

def portal_languages():
    return getToolByName(getSite(), 'portal_languages')
