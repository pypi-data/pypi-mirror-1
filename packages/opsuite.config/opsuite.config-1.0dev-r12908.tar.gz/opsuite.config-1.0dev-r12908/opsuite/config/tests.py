from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

import unittest
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc


@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import opsuite.config
    zcml.load_config('configure.zcml', opsuite.config)
    fiveconfigure.debug_mode = False

setupPackage()
PloneTestCase.setupPloneSite()


class ConfigTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests
    """
    
    def afterSetUp(self):
        self.portal.portal_quickinstaller.installProduct("opsuite.config")
        super(self.__class__, self).afterSetUp()
    

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'initial_globals.txt', package='opsuite.config',
            test_class=ConfigTestCase),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
