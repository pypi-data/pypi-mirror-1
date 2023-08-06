import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

ptc.setupPloneSite()

import Products.pipbox

ztc.installProduct('pipbox')

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.pipbox)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['pipbox'])


class TestCase(ptc.FunctionalTestCase):
    pass

def test_suite():
    return unittest.TestSuite([

    ztc.FunctionalDocFileSuite(
        'README.txt', package='Products.pipbox.tests',
        test_class=TestCase,
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
