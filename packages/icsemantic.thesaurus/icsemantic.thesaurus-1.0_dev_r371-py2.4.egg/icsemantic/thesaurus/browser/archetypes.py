from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.CMFPlone.utils import safe_unicode
from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from incrementalSearchSelectWidget import *
from Products.Archetypes.utils import unique
from pyThesaurus.Thesaurus import ConceptsConflict
import cgi

class IncrementalSearchSelectWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'size'  : 5,
        'roleBasedAdd' : True,
        })

    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        kwargs['macro'] = "incrementalSearchSelectArchetypesWidget"
        super(IncrementalSearchSelectWidget, self).__init__(**kwargs)

    def __call__(self, widgetName, mode='edit', arg=None):
        #html = self.template()
        self.set_name(widgetName)
        return super(IncrementalSearchSelectWidget, self).__call__(widgetName, mode, arg)

    security.declarePublic('process_form')    
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """process keywords from form where this widget has a list of
        available keywords and any new ones"""
        name = field.getName()
        new_keywords_string = form.get('%s' % name, empty_marker)
        if new_keywords_string is empty_marker:
            new_keywords = []
        else:
            new_keywords = self.terms_with_language(self.without_duplicated_and_empty(lstrip(new_keywords_string.split(","))))
            if self.allowToAddNewTermsToThesaurus():
                self.addNewTermsToThesaurus(new_keywords)

        value = new_keywords

        if not value and emptyReturnsMarker: return empty_marker

        return value, {}
    
    def without_duplicated_and_empty(self, aList):
        return dict([ (term,True) for term in aList if term ]).keys()
        
    def safe_name(self):
        return safe_name(self.name)
    
    def name(self):
        return _name
    
    def set_name(self, aName):
        _name = aName
    
    def getInputValue(self):
        return self.selectedConcepts()
    
    def selectedConcepts(self):
        return [ int(strcid) for strcid in self.request["%s_concepts" % safe_name(self.name)].split(",") ]
    
    def termsToConcepts(self, terms):
        return [ self.conceptWithPreferedTerm(term) for term in terms ]
    
    def terms_with_language(self, terms):
        return [ self.term_with_language(term) for term in terms ]
    
    def term_with_language(self, aTerm):
        if not "@" in aTerm:
            return aTerm + "@" + preferredLanguage()
        else:
            return aTerm
    
    def conceptWithPreferedTerm(self, aTerm):
        cids = [ cid for cid in self.conceptsWithTerm(aTerm) if aTerm in thesaurus_utility()[cid].get_prefered(supportedLanguages()) ]
        if len(cids) > 0:
            concept = str(cids[0])
        else:
            concept = aTerm
        return concept
    
    def conceptsWithTerm(self, aTerm):
        try:
            cids = thesaurus_utility()(aTerm)
        except IndexError:
            cids = []
        return cids
    
    def listToString(self, aList):
        if len(aList) == 0:
            aString = ""
        else:
            aString = ", ".join(aList) + ", "
        return aString
    
    def addNewTermsToThesaurus(self, new_terms):
        for term in self.termsToConcepts(new_terms):
            try:
                cid = int(term) #it is a concept
            except: #it is a term
                try:
                    thesaurus_utility().append_term(term)
                except ConceptsConflict, e:
                    print "Warning: The term " + str(e.value) + " already exist in the thesaurus."
    
    def allowToAddNewTermsToThesaurus(self):
        return True
