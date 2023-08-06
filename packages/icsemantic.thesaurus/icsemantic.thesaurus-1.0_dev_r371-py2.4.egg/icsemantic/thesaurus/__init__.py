# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 358 2008-07-29 18:56:21Z flarumbe $
#
# end: Platecom header

from StringIO import StringIO
from Products.CMFCore.DirectoryView import registerDirectory
from zope.component import getUtility
from replaceKeywordsWidget import replace_keywords_widget_at_metadata_page

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    # Apply monkey patches
    import patches
    
    if keywords_incrementalsearchwidget(context._ProductContext__app):
        replace_keywords_widget_at_metadata_page(StringIO())
    else:
        print "Warning: Keywords Incremental Search Widget is disabled."

def exist_keywords_incrementalsearchwidget_property(app):
    return 'icsemantic.thesaurus.configuration.keywords_incrementalsearchwidget' in app.propertyIds()

def keywords_incrementalsearchwidget(app):
    if exist_keywords_incrementalsearchwidget_property(app):
        return app['icsemantic.thesaurus.configuration.keywords_incrementalsearchwidget']
    else:
        return False

def add_keywords_incrementalsearchwidget_property_ifnotexists(app):
    if not exist_keywords_incrementalsearchwidget_property(app):
        app._setProperty('icsemantic.thesaurus.configuration.keywords_incrementalsearchwidget', True)

def update_keywords_incrementalsearchwidget_property(app, value):
    app._updateProperty('icsemantic.thesaurus.configuration.keywords_incrementalsearchwidget', value)
