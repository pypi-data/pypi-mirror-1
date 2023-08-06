# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: base.py 308 2008-06-26 17:46:59Z flarumbe $
#
# end: Platecom header
"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of Plone's
products are loaded, and a Plone site will be created. This happens at module
level, which makes it faster to run each test, but slows down test runner
startup.
"""
import os, sys
from App import Common

from zope.app.component.hooks import setSite

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.thesaurus.interfaces import IThesaurus
from icsemantic.catalog.config import *
from pyThesaurus.Concept import Concept
from icsemantic.langfallback.tests import utils

from icsemantic.thesaurus.config import *

ztc.installProduct('GenericSetup')
ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')

#
# When ZopeTestCase configures Zope, it will *not* auto-load products in
# Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e. not in
# the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#

@onsetup
def setup_icsemantic_thesaurus():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', PACKAGE)
    fiveconfigure.debug_mode = False

    # XXX monkey patch everytime (until we figure out the problem where
    #   monkeypatch gets overwritten somewhere)
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)
#        ztc.installProduct(PROJECTNAME)

        # MONKEYPATCH: arregla los problemas con el
        # control panel y la instalacion de Five...
        import App
        App.ApplicationManager.ApplicationManager.Five=utils.Five

        # MONKEYPATCH: arregla los problemas con el
        # HTTP_REFERER en los tests funcionales. Tiene la
        # contra de enviarnos al raiz del plone cada vez
        # que un metodo depende de esa variable, pero es
        # mejor que morir con una excepcion o llenar los
        # tests de try blocks...
        ztc.zopedoctest.functional.http=utils.http


    except ImportError:
        # Not needed in Plone 3
        ztc.installPackage('icsemantic.core')
        ztc.installPackage('icsemantic.langfallback')
        ztc.installPackage(PROJECTNAME)

setup_icsemantic_thesaurus()

ptc.setupPloneSite(products=[PROJECTNAME,])

# TODO: this is copied from icsemantic.catalog. We should move this to
# icsemantic.core.tests.base and use it from there.
def add_test_thesaurus(context):
    """Fill the thesaurus local utility with some useful information"""

    # XXX: this shouldn't be necesary, but doesn't look like something
    # to take care in this package.
    setSite(context)

    t = thesaurus_utility()
    c = Concept(et = ["fútbol@es", "balón pie@es", "soccer@en", "football@en",
                      "football@fr"])
    t.append_concept(c)
    t.append_term("mundial@es", rt=["fútbol@es"], automatic=False)

    t.append_term("pelota@es", rt=["balón pie@es"], contexts=['publicidad'],
                  automatic=False)


class icSemanticTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit
    test cases.
    """

    def loadThesaurus(self, filename, language="en", format='SKOSCore', encoding='latin1'):
        self.thesaurus_utility().clean()
        self.thesaurus_utility().load(filename, language, format=format, encoding=encoding)

    def thesaurus_utility(self):
        return thesaurus_utility()
    
    def _where_are_different(self, aString, anotherString):
        if aString == anotherString:
            print "Both strings are equal."
        else:
            print "String 1:"
            print aString
            print "String 2:"
            print anotherString
            print "length 1: %d" % len(aString)
            print "length 2: %d" % len(anotherString)
            for i in range(min(len(aString), len(anotherString))):
                if aString[i] != anotherString[i]:
                    print "first difference at: %d" % i
                    print "character 1: '%c'" % aString[i]
                    print "character 2: '%c'" % anotherString[i]
                    break

class icSemanticFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
    def setUp(self):
        super(ptc.FunctionalTestCase, self).setUp()
        add_test_thesaurus(self.portal)