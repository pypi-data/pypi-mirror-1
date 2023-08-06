# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_mailmanplone.py 244 2008-06-11 19:45:48Z crocha $
#
# end: Platecom header
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from iccommunity.mailman.config import *
import base

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocTestSuite(
            module=PACKAGENAME + '.Extensions.install',
            test_class=base.icCommunityTestCase),

        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package=PACKAGENAME,
            test_class=base.icCommunityTestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', package=PACKAGENAME,
            test_class=base.icCommunityFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
