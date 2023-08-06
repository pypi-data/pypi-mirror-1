import unittest

from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite
from zope.app.testing import placelesssetup
from Testing import ZopeTestCase as ztc

# these are used by setup
from five.intid.site import add_intids
from five.intid.lsm import USE_LSM
from OFS.SimpleItem import SimpleItem

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import nfg.ratedreactions

@onsetup
def _setUp():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
            nfg.ratedreactions)
    fiveconfigure.debug_mode = False
    ztc.installPackage('nfg.ratedreactions')

_setUp()
ptc.setupPloneSite(products=['nfg.ratedreactions'])

class Demo(SimpleItem):
    def __init__(self, obid):
        self.id = obid
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

def contentSetUp(app):
    add_intids(app)
    for i in range(9):
        obid = 'ob%d' % i
        ob_object = Demo(obid)
        app._setObject(obid, ob_object)


optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE |doctest.ELLIPSIS


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocFileSuite(
                'README.txt', package='nfg.ratedreactions',
                test_class=ptc.PloneTestCase,
                optionflags=optionflags),

        DocTestSuite(
                module='nfg.ratedreactions.db',
                optionflags=optionflags),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='nfg.ratedreactions',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='nfg.ratedreactions',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
