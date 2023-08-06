from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.core.vocabularies import LanguagesVocabularyFactory
import cgi

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


class IncrementalSearchSelectWidget(SimpleInputWidget):

    template = ViewPageTemplateFile('templates/incrementalSearchSelect-widget.pt')

    def __init__(self, context, request, thesaurus_context="", thesaurus_languages=[]):
        super(IncrementalSearchSelectWidget, self).__init__(context, request)
        self.extra = " autocomplete='off' concepts='' onfocus='timerIncrementalSearchSelect(this.id);' onkeypress='return keypressed(this.id, event)' size='50'"
        self._thesaurus_context = thesaurus_context
        self._thesaurus_languages = thesaurus_languages

    def __call__(self):
        html = self.template()
        html += super(IncrementalSearchSelectWidget, self).__call__()
        html += '<input type="hidden" name="%s_autocompletedExpression" id="%s_autocompletedExpression" value="" concepts="">' % (safe_name(self.name), safe_name(self.name))
        html += '<input type="hidden" name="%s_concepts" id="%s_concepts" value="">' % (safe_name(self.name), safe_name(self.name))
        html += '<input type="hidden" name="%s_autocompleteConceptsAction" id="%s_autocompleteConceptsAction" class="incrementalSearchSelect" widgetName="%s" value="" concepts="">' % (self.name, self.name, self.name)
        html += '<input type="hidden" name="%s_chooseSelectedConceptAction" id="%s_chooseSelectedConceptAction" class="chooseSelectedConcept" widgetName="%s" value="" concepts="">' % (self.name, self.name, self.name)
        html += '<div id="div_%s"></div>' % safe_name(self.name) #TODO: replace to query
        return html
    
    def getInputValue(self):
        return self.selectedConcepts()
    
    def selectedConcepts(self):
        return [ int(strcid) for strcid in self.request["%s_concepts" % safe_name(self.name)].split(",") ]

class IncrementalSearchSelectAzax(AzaxBaseView):

    def autocompleteConcepts(self, widgetName, searchExpression):
        IKSSCoreCommands(self).replaceInnerHTML('div#div_%s' % safe_name(widgetName), self.html_someConceptsList(searchExpression.split(",")))
        return self.render()

    def chooseSelectedConcept(self, widgetName, searchExpression, concepts):
        #TODO: probar .setAttribute
        (newSearchExpression, selectedConcept) = self.html_conceptSelectedSearchExpression(searchExpression)
        IKSSCoreCommands(self).setAttribute('input#%s_autocompletedExpression' % safe_name(widgetName), "value", newSearchExpression)
        if selectedConcept != None:
            if concepts != "":
                concepts += "," + str(selectedConcept)
            else:
                concepts = str(selectedConcept)
            IKSSCoreCommands(self).setAttribute('input#%s_autocompletedExpression' % safe_name(widgetName), "concepts", concepts)
        return self.render()

    def languages(self):
        return [ language.value for language in LanguagesVocabularyFactory(self.context) ]

    def html_conceptSelectedSearchExpression(self, searchExpression):
        search_words = searchExpression.split(",")
        last_word = search_words[len(search_words) - 1].lstrip()
        if last_word == "":
            newSearchExpression = searchExpression
            selectedConcept = None
        else:
            results = self.query(last_word)
            if len(results) > 0:
                selected_word = results[0][0]
                selectedConcept = results[0][1]
                search_words[len(search_words) - 1] = selected_word
                newSearchExpression = (u", ").join(self.lstrip(search_words)) + (u", ")
            else:
                newSearchExpression = searchExpression
                selectedConcept = None
        return (safe_unicode(newSearchExpression), selectedConcept)
    
    def lstrip(self, words):
        return [ word.lstrip() for word in words ]

    def html_someConceptsList(self, search_words):
        last_word = search_words[len(search_words) - 1].lstrip()
        html = ""
        if last_word != "":
            results = self.query(last_word)
            if len(results) > 0:
                selected_word = results[0][0]
            else:
                selected_word = ""
            current_input = last_word

            html += "<table cellspacing='0' cellpadding='0' border='0'>"
            html += "    <tr>"
            html += "        <td><div id='searchResults' class='incrementalSearchSelectResults'>"
            for (term, cid) in results:
                html += self.html_word_item(term, selected_word, current_input)
            if len(results) > self.max_results():
                html += "            ...<br>"
            html += "            </div></td>"
            html += "        <td height='100%'>"
            if len(results) > self.max_results():
                html += "<table cellspacing='0' cellpadding='0' border='0' height='100%'>"
                html += "                <tr><td style='vertical-align: top'><img src='arrowUp.gif' border='0'></td></tr>"
                html += "                <tr><td style='vertical-align: bottom'><img src='arrowDown.gif' border='0'></td></tr>"
                html += "            </table>"
            else:
                html += "&nbsp;"
            html += "</td>"
            html += "    </tr>"
            html += "</table>"
        return html

    def html_word_item(self, word, selected_word, current_input):
        if word == selected_word:
            return u"			<i>%s</i><br>" % self.html_emphasize_input(word, current_input)
        else:
            return u"			%s<br>" % self.html_emphasize_input(word, current_input)

    def html_emphasize_input(self, word, current_input):
        if current_input != "":
            return safe_unicode((u"<b>" + current_input + u"</b>").join(word.split(current_input)))
        else:
            return safe_unicode(word)
    
    def query(self, search_expression):
        return thesaurus_utility().query(search_expression=search_expression,
                                            narrowedthan = None,
                                            borrowedthan = None,
                                            contexts = [],
                                            languages = self.languages(),
                                            inbranch = None,
                                            hidden = None,
                                            max_results = self.max_results())
    
    def max_results(self):
        return 5

def IncrementalSearchSelectWidgetFactory(context, request, thesaurus_context="", thesaurus_languages=[]):
    return IncrementalSearchSelectWidget(context, request, thesaurus_context, thesaurus_languages)

def safe_name(aString):
    return aString.replace(".", "")