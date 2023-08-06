"""Test icNews.Core setup on installation.
"""

import unittest

from base import icNewsCoreTestCase
from icnews.core.interfaces import IicNewsSite


class TestICNewsCoreSetup(icNewsCoreTestCase):
    """Testing the product setup"""

    def afterSetUp(self):
        """Ran before every unit test"""
        self.qi = self.portal.portal_quickinstaller

    def test_install(self):
        self.failUnless(self.qi.isProductInstalled('icnews.core'))

    def test_site_provides(self):
        self.failUnless(IicNewsSite.providedBy(self.portal))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestICNewsCoreSetup))
    return suite
