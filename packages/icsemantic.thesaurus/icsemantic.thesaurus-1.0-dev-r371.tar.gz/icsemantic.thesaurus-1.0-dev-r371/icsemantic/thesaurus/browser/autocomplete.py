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

from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.core.vocabularies import LanguagesVocabularyFactory
import icsemantic.core.browser.admin

import cgi

class AutoComplete(AzaxBaseView):

    def autocompleteConcepts(self, searchExpression):
        #TODO: probar .setAttribute
        #import ipdb
        #ipdb.set_trace()
        IKSSCoreCommands(self).replaceInnerHTML('div#searchResults', 'Resultado de "' + cgi.escape(safe_unicode("<br>".join(searchExpression.split(",")))) + '"')
        return self.render()
