# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import icsemantic.langfallback
PACKAGE = icsemantic.langfallback

PROJECTNAME = "icsemantic.langfallback"
PACKAGENAME = "icsemantic.langfallback"

DEPENDENCIES = ['LinguaPlone',
                'icsemantic.core',]

if HAS_PLONE3:
    DEPENDENCIES.insert(0, 'plone.browserlayer')

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

GLOBALS = globals()
