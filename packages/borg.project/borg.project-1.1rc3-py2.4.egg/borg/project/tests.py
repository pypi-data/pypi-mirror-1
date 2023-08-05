import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_borg_project():
    """Set up the additional products required for the borg.project tests.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the borg.project package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import borg.project
    zcml.load_config('configure.zcml', borg.project)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Notice the extra package=True argument passed to 
    # installProduct() - this tells it that these packages are *not* in the
    # Products namespace.
    
    ztc.installPackage('borg.localrole')
    ztc.installPackage('borg.project')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Centrepoint package. Then, we let 
# PloneTestCase set up this product on installation.

setup_borg_project()
ptc.setupPloneSite(products=['borg.project'])

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'README.txt', package='borg.project',
            test_class=ptc.FunctionalTestCase,
            optionflags=(doctest.ELLIPSIS | 
                         doctest.NORMALIZE_WHITESPACE)),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
