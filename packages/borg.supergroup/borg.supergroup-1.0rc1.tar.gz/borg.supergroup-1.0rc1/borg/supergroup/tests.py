import unittest
import doctest

from zope.interface import implements
from zope.app.testing import placelesssetup
import zope.testing.doctest

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import borg.supergroup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', borg.supergroup)
    fiveconfigure.debug_mode = False
    ztc.installPackage('borg.supergroup')
    
setup_product()
ptc.setupPloneSite(products=['borg.supergroup'])

def test_suite():
    suite = []

    suite.extend([
        ztc.ZopeDocFileSuite(
                    'integration.txt', package='borg.supergroup',
                    test_class=ptc.FunctionalTestCase,
                    optionflags=(doctest.ELLIPSIS |
                                 doctest.NORMALIZE_WHITESPACE)),
        ])

    # Add the tests that register adapters at the end

    suite.extend([
        zope.testing.doctest.DocTestSuite(borg.supergroup.plugin,
            setUp=placelesssetup.setUp(),
            tearDown=placelesssetup.tearDown()),
        ])


    return unittest.TestSuite(suite)