# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_property_langview_language.py 282 2008-06-16 13:04:38Z crocha $
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

class TestPropertyLangviewLanguage(base.icSemanticTestCase):
    
    def testInstalled(self):
        """
        >>> memberdata = self.portal.portal_memberdata
        >>> [property for property in memberdata.propertyMap() if property['id'] == 'icsemantic.preferred_languages']
        [{'type':...'lines', 'id': 'icsemantic.preferred_languages'}]
        """

    def testAssignValue(self):
        """
        >>> portal = self.portal
        >>> memberdata = self.portal.portal_memberdata
        >>> member1 = portal.portal_registration.addMember('test1', 'test1')
        >>> member1
        <MemberData at /plone/portal_memberdata/test1 used for /plone/acl_users>
    
        >>> member1.setMemberProperties({'icsemantic.preferred_languages': ('en', 'es', 'it')})
        >>> member1.getProperty('icsemantic.preferred_languages')
        ('en', 'es', 'it')
        """

    def testUnInstalled(self):
        """
        >>> from icsemantic.langfallback.config import *
        >>> qi = self.portal.portal_quickinstaller
        >>> qi.uninstallProducts((PACKAGENAME,))
        >>> memberdata = self.portal.portal_memberdata
        >>> [property for property in memberdata.propertyMap() if property['id'] == 'icsemantic.preferred_languages']
        []
        """
        
def test_suite():
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocTestSuite(
            test_class=TestPropertyLangviewLanguage),

        # Integration tests that use PloneTestCase
        ztc.FunctionalDocFileSuite(
            'test_property_langview_language.txt', package=PACKAGENAME + '.tests',
            test_class=base.icSemanticFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
