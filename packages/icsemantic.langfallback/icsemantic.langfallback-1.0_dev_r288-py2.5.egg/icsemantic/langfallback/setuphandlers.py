# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setuphandlers.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
""" CMFDefault setup handlers.

$Id: setuphandlers.py 236 2008-06-10 20:28:23Z crocha $
"""
from StringIO import StringIO

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from icsemantic.core.interfaces import IContentTypesMultilingualPatcher

def patchPortalTypes(portal, out):
    """
    """
    archetype_tool = getToolByName( portal, 'archetype_tool')
#    import pdb;pdb.set_trace()
    for atype in archetype_tool.listTypes():
        print >> out, 'Patching getters for %s' % atype
        if hasattr(atype, 'getLanguage'):
            ccpatcher = getUtility(IContentTypesMultilingualPatcher)
            ccpatcher.patch(atype)

def unpatchPortalTypes(portal, out):
    """
    """
    archetype_tool = getToolByName( portal, 'archetype_tool')
    for atype in archetype_tool.listTypes():
        if hasattr(atype, 'getLanguage'):
            ccpatcher = getUtility(IContentTypesMultilingualPatcher)
            ccpatcher.unpatch(atype)

def importVarious(context):
    """ Import various settings.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()
    out = StringIO()
    logger = context.getLogger("icsemantic.langfallback")

#    patchPortalTypes(site, out)

    print >> out, 'Various settings imported.'

    logger.info(out.getvalue())
    return out.getvalue()

def unimportVarious(context):
    """ Import various settings.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()

    return 'Various settings imported.'
