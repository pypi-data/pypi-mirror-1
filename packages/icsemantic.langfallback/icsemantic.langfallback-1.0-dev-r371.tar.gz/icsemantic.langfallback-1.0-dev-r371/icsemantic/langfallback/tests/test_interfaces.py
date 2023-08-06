# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_interfaces.py 243 2008-06-11 19:45:26Z crocha $
#
# end: Platecom header
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from icsemantic.langfallback.config import *
import base

class TestInterfaces(base.icSemanticTestCase):
    """
    """
    
def test_suite():
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocTestSuite(
                module=PACKAGENAME + '.interfaces',
                test_class=TestInterfaces),

        # Integration tests that use PloneTestCase
        ztc.FunctionalDocFileSuite(
            'test_interfaces.txt', package=PACKAGENAME + '.tests',
            test_class=base.icSemanticFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
