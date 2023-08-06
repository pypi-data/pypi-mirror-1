import unittest

from icnews.acquire.tests.base import ICNewsAcquireTestCase


class TestAdqnews(ICNewsAcquireTestCase):
    """Testing the product setup"""

    def afterSetUp(self):
        """Ran before every unit test"""
        self.qi = self.portal.portal_quickinstaller
        self.catalog = self.portal.portal_catalog
        self.types = self.portal.portal_types

    def test_type_installed(self):
        """Test that the Adqnews type is instaled."""
        adqnews_fti = getattr(self.types, 'Adqnews')
        self.assertEquals('Adqnews', adqnews_fti.title)

    def test_fields(self):
        """Test fields"""
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Adqnews', 'adqnews1')
        fields = ['title', 'source', 're', 'description', 'encoding', 'store']

        object_fields = self.portal.adqnews1.schema.fields()
        object_fields = [i.getName() for i in object_fields]

        for field in fields:
            self.failUnless(field in object_fields)

    def test_global_allow(self):
        """Test that Adqnews is globally allowed"""
        adqnews_fti = getattr(self.types, 'Adqnews')
        self.failUnless(adqnews_fti.global_allow)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAdqnews))
    return suite
