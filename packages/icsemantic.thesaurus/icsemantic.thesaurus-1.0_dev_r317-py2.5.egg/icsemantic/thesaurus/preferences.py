# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: preferences.py 306 2008-06-24 19:40:34Z flarumbe $
#
# end: Platecom header
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty

import interfaces

class icSemanticManagementThesaurusUpload:
    implements(interfaces.IicSemanticManagementThesaurusUpload)

    def __init__(self, context):
        """
        """
        self.context = context

    def __call__(self):
        pass

    thesaurus_file = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['thesaurus_file'])
    default_language = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['default_language'])
    thesaurus_context = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['thesaurus_context'])
    thesaurus_format = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['thesaurus_format'])
    encoding = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['encoding'])
    new = FieldProperty(interfaces.IicSemanticManagementThesaurusUpload['new'])

class icSemanticVerticalSelectTest:
    implements(interfaces.IicSemanticVerticalSelectTest)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        pass

    vertical_select = FieldProperty(interfaces.IicSemanticVerticalSelectTest['vertical_select'])

def thesaurus_upload_adapter(context):
    return icSemanticManagementThesaurusUpload(context)

def vertical_select_test_adapter(context):
    return icSemanticVerticalSelectTest(context)