# Test installation code

from Products.pluggablecatalog.tests import common
common.setupPloneSite()

from Products.PloneTestCase import PloneTestCase

from Products.pluggablecatalog import tool
from Products.pluggablecatalog.Extensions import install

class Test(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def testCatalogExists(self):
        install.install(self.portal)
        self.failUnless(
            isinstance(self.portal.portal_catalog.aq_base, tool.CatalogTool))
        
    def testReinstall(self):
        # A reinstall shouldn't touch the existing catalog.
        install.install(self.portal)
        catalog = self.portal.portal_catalog.aq_base
        install.install(self.portal)
        self.failUnless(catalog is self.portal.portal_catalog.aq_base)

    def testQuickInstallable(self):
        qi = self.portal.portal_quickinstaller
        qi.installProducts(('pluggablecatalog',))
        self.failUnless(
            isinstance(self.portal.portal_catalog.aq_base, tool.CatalogTool))

    def testReindex(self):
        # Test that after reinstall the reindexing has done its job
        self.folder.invokeFactory('Document', 'mydocument')
        mydoc = self.folder.mydocument
        mydoc.setTitle("My Document")
        mydoc.reindexObject()

        # Assert that it's in the catalog now
        brains = self.portal.portal_catalog(Title="My Document")
        self.assertEquals(len(brains), 1)
        self.failUnless(brains[0].getObject().aq_base is mydoc.aq_base)

        # Install pluggablecatalog in the site; still in the catalog?
        install.install(self.portal)        
        brains = self.portal.portal_catalog(Title="My Document")
        self.assertEquals(len(brains), 1)
        self.failUnless(brains[0].getObject().aq_base is mydoc.aq_base)
        self.assertEquals(brains[0].Title, "My Document")
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite
