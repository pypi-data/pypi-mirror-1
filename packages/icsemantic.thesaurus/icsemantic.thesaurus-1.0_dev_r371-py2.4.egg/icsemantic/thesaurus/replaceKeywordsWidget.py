from Products.CMFCore.utils import getToolByName
from browser.archetypes import IncrementalSearchSelectWidget
from Products.Archetypes.Widget import KeywordWidget

def replace_keywords_widget_at_metadata_page(out):
    print >> out, "Replacing keywords widget to incremental search widget at metadata page..."
    from Products.ATContentTypes.content.document import ATDocument
    ATDocument('widget-temp-document').schema['subject'].widget = IncrementalSearchSelectWidget(
                                                                label="Keywords",
                                                                label_msgid="label_keywords",
                                                                description_msgid="help_keyword",
                                                                i18n_domain="plone")
    print >> out, "Replaced."

def replace_keywords_widget_to_original_at_metadata_page(out):
    print >> out, "Replacing keywords widget to original one at metadata page..."
    from Products.ATContentTypes.content.document import ATDocument
    ATDocument('widget-temp-document').schema['subject'].widget = KeywordWidget(
                                                                    label="Keywords",
                                                                    label_msgid="label_keywords",
                                                                    description_msgid="help_keyword",
                                                                    i18n_domain="plone")
    print >> out, "Replaced."
