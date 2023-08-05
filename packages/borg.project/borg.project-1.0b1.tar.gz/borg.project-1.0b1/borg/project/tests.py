import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

import borg.project

ptc.setupPloneSite()

class ProjectTestCase(ptc.FunctionalTestCase):

    def _setup(self):
        super(ProjectTestCase, self)._setup()
        self.portal.portal_quickinstaller.installProduct('CMFPlacefulWorkflow')
        self.portal.portal_quickinstaller.installProduct('borg.project')

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', borg.project)
            fiveconfigure.debug_mode = False

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'README.txt', package='borg.project',
            test_class=ProjectTestCase,
            optionflags=(doctest.ELLIPSIS | 
                         doctest.NORMALIZE_WHITESPACE |
                         doctest.REPORT_ONLY_FIRST_FAILURE)),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
