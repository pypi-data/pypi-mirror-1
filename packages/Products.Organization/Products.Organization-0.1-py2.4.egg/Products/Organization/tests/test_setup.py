from base import OrganizationTestCase
from example.archetype.interfaces import IOrganization

class TestProductInstall(InstantOrganizationTestCase):

    def afterSetUp(self):
        self.types = ('Organization',)

    def testTypesInstalled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)

    def testPortalFactoryEnabled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_factory.getFactoryTypes().keys(),
                            '%s content type not installed' % t)

class TestInstantiation(OrganizationTestCase):

    def afterSetUp(self):
        # Adding an Organization anywhere - can only be done by a Manager or Portal Owner
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Organization', 'im1')

    def testCreateOrganization(self):
        self.failUnless('im1' in self.portal.objectIds())

    def testOrganizationInterface(self):
        im = self.portal.im1
        self.failUnless(IOrganization.providedBy(im))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    suite.addTest(makeSuite(TestInstantiation))
    return suite
