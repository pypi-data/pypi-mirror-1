# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: install.py 314 2008-06-26 22:02:34Z flarumbe $
#
# end: Platecom header
"""
$Id: install.py 314 2008-06-26 22:02:34Z flarumbe $
"""
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Extensions.utils import install_subskin
from icsemantic.thesaurus.config import *
from icsemantic.thesaurus.interfaces import IThesaurus
from icsemantic.thesaurus.Thesaurus import Thesaurus

def install_configlets( portal, out):
    """
    Method to install platecom user properties...
        @type: portal: PloneSite
        @type out: StringIO

        @rtype: StringIO
        @return: Messages from the GS process
    """
    configTool=getToolByName(portal,'portal_controlpanel',None)
    if configTool:
        for conf in CONFIGLETS:
            configTool.registerConfiglet(**conf)
            out.write('Added configlet %s\n' % conf['id'])

    return out

def install_dependencies( self ):
    """
    Test if everything at DEPENDENCIES gets installed...
        >>> 1
        1
    """
    # If the config contains a list of dependencies, try to install
    # them.  Add a list called DEPENDENCIES to your custom
    # AppConfig.py (imported by config.py) to use it.
    out = StringIO()
    portal = getToolByName(self, 'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in DEPENDENCIES:
        print >> out, "Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)

    return out

def install( self ):
    """
    External module to install the product...
        @type self: PloneSite
        @param self: The Plone site object

        @rtype: StringIO
        @return: Messages from the install process

    some tests here...
        >>> from icsemantic.thesaurus.config import *
        >>> qi = self.portal.portal_quickinstaller
        >>> installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
        >>> PACKAGENAME in installed
        True

    """
    
    out = StringIO()
    print >> out, "Installing Dependencies"
    install_dependencies(self)

    setup_tool = getToolByName(self, 'portal_setup')
    if shasattr(setup_tool, 'runAllImportStepsFromProfile'):
        # Plone 3
        pass
    else:
        # Plone 2.5.  Would work on 3.0 too, but then it gives tons of
        # DeprecationWarnings when running the tests, causing failures
        # to drown in the noise.
        pass

    install_thesaurus_utility(self, out)

    install_subskin(self, out, GLOBALS)

    install_resources(self, out)

    return out.getvalue()

def install_thesaurus_utility(self, out):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    sm = portal.getSiteManager()
    if not sm.queryUtility(IThesaurus, name=''):
	try:
            sm.registerUtility(Thesaurus(),IThesaurus,'')
	except:
            sm.registerUtility(IThesaurus,Thesaurus(),'')
    
    out.write("Adding Thesaurus Utility\n")

def install_resources(self, out):
    print >> out, "Adding incremental search widget css and kss..."
    css_all = [ 'portal_skins/icsemantic.thesaurus/incrementalSearchSelectWidget.css' ]
    kss_all = [ 'portal_skins/icsemantic.thesaurus/incrementalSearchSelectWidget.kss' ]
    csstool = getToolByName(self, 'portal_css')
    for css in css_all:
        csstool.manage_addStylesheet(
            id = css,
            rel = 'stylesheet',
            rendering = 'link',
            enabled = True,
            cookable = True,
            )
    for kss in kss_all:
        csstool.manage_addStylesheet(id=kss,
            rel='kukit',
            rendering = 'link',
            enabled=True,
            cookable=False,
            )
    print >> out, "Added."

def uninstall( self ):
    """
    Test if everything gets installed...
        >>> 1
        1
    """
    out = StringIO()

    print >> out, "Uninstalling"

    return out.getvalue()
