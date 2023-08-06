"""Installation
"""
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Extensions.utils import install_subskin

from icnews.core.config import *


def install_dependencies( portal, out):
    """
    Method to install dependencies...
        @type portal: PloneSite
        @param portal: The Plone site object
        @type out: StringIO
        @param out: The object to append the output

        @rtype: StringIO
        @return: Messages from the GS process

    some tests here...

    """
    # If the config contains a list of dependencies, try to install
    # them.  Add a list called DEPENDENCIES to your custom
    # AppConfig.py (imported by config.py) to use it.
    quickinstaller = portal.portal_quickinstaller
    for dependency in DEPENDENCIES:
        print >> out, "Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)

    return out

def import_gs_profiles( portal, out):
    """
    Method to install GS profiles...
        @type portal: PloneSite
        @param portal: The Plone site object
        @type out: StringIO
        @param out: The object to append the output

        @rtype: StringIO
        @return: Messages from the GS process

    some tests here...
        >>> from icnews.core.config import *
        >>> psetup = self.portal.portal_setup

    just test we have registered the profile...
        >>> profilename = PROJECTNAME + ':default'
        >>> PACKAGENAME in [profile['product'] for profile in psetup.listProfileInfo()]
        True
        >>> profilename in [profile['id'] for profile in psetup.listProfileInfo()]
        True

    now we can test some stuff modified but that template...
        >>> 'icNews' in [ai.getTitle() for ai in portal.portal_actionicons.listActionIcons()]
        True

    No se porque este no anda, anda bien en el test funcional...
        >>> # [ai['name'] for ai in portal.portal_controlpanel.listActionInfos()] True


    """
    # Run all import steps
    setup_tool = getToolByName(portal, 'portal_setup')
    profile_name = 'profile-' + PROJECTNAME + ':default'
    if shasattr(setup_tool, 'runAllImportStepsFromProfile'):
        # Plone 3
        print >> out, setup_tool.runAllImportStepsFromProfile(profile_name)
    else:
        # Plone 2.5.  Would work on 3.0 too, but then it gives tons of
        # DeprecationWarnings when running the tests, causing failures
        # to drown in the noise.
        old_context = setup_tool.getImportContextID()
        print >> out, setup_tool.setImportContext(profile_name)
        print >> out, setup_tool.runAllImportSteps()
        print >> out, setup_tool.setImportContext(old_context)

    return out

def install( self ):
    """
    """
    out = StringIO()
    portal = getToolByName(self,'portal_url').getPortalObject()

    install_subskin(self, out, GLOBALS)

    print >> out, "Installing Dependencies"
    res = install_dependencies( portal, out)
    print >> out, res or 'no output'

    print >> out, "Import GS Profiles"
    res = import_gs_profiles( portal, out)
    print >> out, res or 'no output'

    return out.getvalue()
