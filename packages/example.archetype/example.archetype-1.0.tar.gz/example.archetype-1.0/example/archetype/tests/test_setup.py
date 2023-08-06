from base import InstantMessageTestCase
from example.archetype.interfaces import IInstantMessage

class TestProductInstall(InstantMessageTestCase):

    def afterSetUp(self):
        self.types = ('InstantMessage',)

    def testTypesInstalled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)

    def testPortalFactoryEnabled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_factory.getFactoryTypes().keys(),
                            '%s content type not installed' % t)

class TestInstantiation(InstantMessageTestCase):

    def afterSetUp(self):
        # Adding an InstantMessage anywhere - can only be done by a Manager or Portal Owner
        self.setRoles(['Manager'])
        self.portal.invokeFactory('InstantMessage', 'im1')

    def testCreateInstantMessage(self):
        self.failUnless('im1' in self.portal.objectIds())

    def testInstantMessageInterface(self):
        im = self.portal.im1
        self.failUnless(IInstantMessage.providedBy(im))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    suite.addTest(makeSuite(TestInstantiation))
    return suite
