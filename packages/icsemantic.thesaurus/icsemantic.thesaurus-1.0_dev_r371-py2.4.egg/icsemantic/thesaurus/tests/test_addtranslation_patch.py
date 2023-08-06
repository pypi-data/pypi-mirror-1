"""Tests
"""
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from icsemantic.thesaurus.config import *
import base

class FunctionalTestConfiglets(base.icSemanticFunctionalTestCase):
    """
    """

def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase
        ztc.FunctionalDocFileSuite(
            'test_addtranslation_patch.txt',
            package=PACKAGENAME + '.tests',
            test_class=FunctionalTestConfiglets),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
