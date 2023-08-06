from Testing import ZopeTestCase as ztc
from zope.testing.doctestunit import DocFileSuite
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from collective.testcaselayer import ptc as tcl_ptc
import unittest


DEPS = ('MimetypesRegistry', 'PortalTransforms', 'Archetypes', 'ATContentTypes', 'kupu')
for product in DEPS:
    ztc.installProduct(product, 1)


class InstallLayer(tcl_ptc.BasePTCLayer):

   def afterSetUp(self):
       import collective.updatelinksoncopy
       zcml.load_config('configure.zcml',
                        collective.updatelinksoncopy)


class TestCase(ptc.FunctionalTestCase):
    def afterSetUp(self):
        portal = self.portal
        self.setRoles(['Manager',])
        self.kupu = portal.kupu_library_tool
        self.kupu.configure_kupu(captioning=True, linkbyuid=True)


ptc.setupPloneSite(products=['ATContentTypes', 'kupu'])
install_layer = InstallLayer([ptc.FunctionalTestCase.layer])

def test_suite():
    suite = (
        ztc.ZopeDocFileSuite(
            'handlers.txt', package='collective.updatelinksoncopy',
            test_class=TestCase),
        DocFileSuite(
            'handlers.py', package='collective.updatelinksoncopy',
            ),
        )

    suite[0].layer = install_layer
    return unittest.TestSuite(suite)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
