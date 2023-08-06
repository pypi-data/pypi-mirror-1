# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: base.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of Plone's
products are loaded, and a Plone site will be created. This happens at module
level, which makes it faster to run each test, but slows down test runner
startup.
"""
import os, sys
from App import Common

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr

from icsemantic.langfallback.config import *

import utils

import doctest
OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

#
# When ZopeTestCase configures Zope, it will *not* auto-load products in
# Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e. not in
# the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#

if HAS_PLONE3:
    ztc.installProduct('plone.browserlayer')

ztc.installProduct('GenericSetup')
ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')

@onsetup
def setup_icsemantic_langfallback():
    ztc.installProduct('Five')
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', PACKAGE)
    fiveconfigure.debug_mode = False

    # MONKEYPATCH: everytime (until we figure out the problem where
    #   monkeypatch gets overwritten somewhere)
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)

        # MONKEYPATCH: arregla los problemas con el
        # control panel y la instalacion de Five...
        import App
        App.ApplicationManager.ApplicationManager.Five=utils.Five

        # MONKEYPATCH: arregla los problemas con el
        # HTTP_REFERER en los tests funcionales. Tiene la
        # contra de enviarnos al raiz del plone cada vez
        # que un metodo depende de esa variable, pero es
        # mejor que morir con una excepcion o llenar los
        # tests de try blocks...
        ztc.zopedoctest.functional.http=utils.http
    except ImportError:
        # Not needed in Plone 3
        ztc.installPackage(PROJECTNAME)

setup_icsemantic_langfallback()

ptc.setupPloneSite(products=[PROJECTNAME,])

class icSemanticTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit
    test cases.
    """

class icSemanticFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
    def afterSetUp(self):
        # Run all import steps
        setup_tool = getToolByName(self.portal, 'portal_setup')
        profile_name = 'profile-' + PROJECTNAME + ':tests'
        if shasattr(setup_tool, 'runAllImportStepsFromProfile'):
            # Plone 3
            setup_tool.runAllImportStepsFromProfile(profile_name)
        else:
            # Plone 2.5.  Would work on 3.0 too, but then it gives tons of
            # DeprecationWarnings when running the tests, causing failures
            # to drown in the noise.
            old_context = setup_tool.getImportContextID()
            setup_tool.setImportContext(profile_name)
            setup_tool.runAllImportSteps()
            setup_tool.setImportContext(old_context)

        super(icSemanticFunctionalTestCase, self).afterSetUp()
