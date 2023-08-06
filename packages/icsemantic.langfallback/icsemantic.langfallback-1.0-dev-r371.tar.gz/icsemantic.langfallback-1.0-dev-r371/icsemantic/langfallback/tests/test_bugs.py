# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_bugs.py 243 2008-06-11 19:45:26Z crocha $
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
import utils

def test_suite():
    suite = unittest.TestSuite()
    filenames = utils.list_functionaltests('bugs')

    for docfile in filenames:
        suite.addTest(ztc.FunctionalDocFileSuite(docfile,
                            package='icsemantic.langfallback.tests',
                            test_class=base.icSemanticFunctionalTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
