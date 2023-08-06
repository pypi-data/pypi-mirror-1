# integration and functional tests
# see http://plone.org/documentation/tutorial/testing/writing-a-plonetestcase-unit-integration-test
# for more information about the following setup

from unittest import TestSuite
from zope.testing import doctest
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import plone.pony
    zcml.load_config('configure.zcml', plone.pony)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(extension_profiles=('plone.pony:default',))


optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite([
        ztc.FunctionalDocFileSuite(
           'README.txt', package='plone.pony',
           test_class=ptc.FunctionalTestCase, optionflags=optionflags),
    ])

