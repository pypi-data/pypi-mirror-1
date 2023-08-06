# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 358 2008-07-29 18:56:21Z flarumbe $
#
# end: Platecom header
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False
import icsemantic.thesaurus
PROJECTNAME = "icsemantic.thesaurus"
PACKAGE = icsemantic.thesaurus
PACKAGENAME = "icsemantic.thesaurus"
DEPENDENCIES = [ 'icsemantic.core', 'icsemantic.langfallback', 'PloneAzax', ]

GLOBALS = globals()
