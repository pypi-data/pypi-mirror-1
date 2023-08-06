import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PortalTaxonomy.tests import TestCase

class TestInstallation(TestCase.PortalTaxonomyTestCase):
    """Ensure product is properly installed"""

    def testSkinLayersInstalled(self):
        self.failUnless('PortalTaxonomy' in self.skins.objectIds())

    def testTypesInstalled(self):
        for t in self.meta_types:
            self.failUnless(t in self.types.objectIds())

    def testPortalFactorySetup(self):
        for t in self.meta_types:
            self.failUnless(t in self.factory.getFactoryTypes())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    return suite

if __name__ == '__main__':
    framework()
