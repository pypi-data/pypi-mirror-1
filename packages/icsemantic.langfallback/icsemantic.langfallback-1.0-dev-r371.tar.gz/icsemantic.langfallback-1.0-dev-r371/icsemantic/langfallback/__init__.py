# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 243 2008-06-11 19:45:26Z crocha $
#
# end: Platecom header
"""
"""
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.DirectoryView import registerDirectory

from icsemantic.core.interfaces import IicSemanticManagementContentTypes, \
                                      IContentTypesMultilingualPatcher

GLOBALS = globals()

registerDirectory('skins', GLOBALS)

LangviewMessageFactory = MessageFactory('icsemantic.langfallback')

def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
#    import pdb;pdb.set_trace()
#    pcm=getUtility(IicSemanticManagementContentTypes,
#                   name='icSemantic.configuration')
#    ccpatcher = getUtility(IContentTypesMultilingualPatcher)
#    import pdb;pdb.set_trace()
#    for type_name in pcm.fallback_types:
#        ccpatcher.patch(type_name, True)
