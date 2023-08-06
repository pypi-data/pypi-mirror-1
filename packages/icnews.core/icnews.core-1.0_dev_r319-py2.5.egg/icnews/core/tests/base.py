"""Test setup for unit, integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.app.component.hooks import setSite

from icsemantic.langfallback.tests import utils

from icnews.core.config import *

#
# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#

@onsetup
def setup_icnews_core():
    ztc.installProduct('Five')
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', PACKAGE)
    fiveconfigure.debug_mode = False

    # XXX monkey patch everytime (until we figure out the problem where
    # monkeypatch gets overwritten somewhere)
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)

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
        ztc.installPackage(PROJECTNAME)
        pass

setup_icnews_core()

ptc.setupPloneSite(products=[PROJECTNAME,])

class icNewsCoreTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """
    pass

class icNewsCoreFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """
    pass
