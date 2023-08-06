
import doctest
import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import garbas.forum
    zcml.load_config('configure.zcml', garbas.forum)
    fiveconfigure.debug_mode = False
    ztc.installPackage('garbas.forum')

setup_product()
ptc.setupPloneSite(products=['garbas.forum'])


class FunctionalTestCase(ptc.FunctionalTestCase):
    """ functional test case """


def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite('content.txt',
            package='garbas.forum', test_class=FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ztc.ZopeDocFileSuite('notification.txt',
            package='garbas.forum', test_class=FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ztc.ZopeDocFileSuite('browser.txt',
            package='garbas.forum', test_class=FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

