import unittest
from Testing import ZopeTestCase as ztc


from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import collective.habla
    zcml.load_config('configure.zcml', collective.habla)
    fiveconfigure.debug_mode = False

setupPackage()
PloneTestCase.setupPloneSite(extension_profiles=(
    'collective.habla:default',
))


class HablaTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests
    """

def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
           'README.txt', package='collective.habla',
           test_class=HablaTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')





