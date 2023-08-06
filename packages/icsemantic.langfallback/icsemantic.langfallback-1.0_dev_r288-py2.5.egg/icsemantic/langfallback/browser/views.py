# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: views.py 243 2008-06-11 19:45:26Z crocha $
#
# end: Platecom header
"""
"""
from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.ATContentTypes.content.folder import ATFolder

from icsemantic.core.interfaces import IicSemanticManagementContentTypes, \
                                      IContentTypesMultilingualPatcher

class MultiLanguages(BrowserView):
    """
    """

    def __init__(self, context, request):
        """
        """
        #self.context = context
        self.context=context
        self.request = request
#        import pdb;pdb.set_trace()
        self.languages = [] # TODO: use some languages adapter
#        import pdb;pdb.set_trace()
#        pcm=getUtility(IicSemanticManagementContentTypes,
#                       name='icSemantic.configuration')
#        ccpatcher = getUtility(IContentTypesMultilingualPatcher)
#        for type_name in pcm.fallback_types:
#            ccpatcher.patch(type_name, True)

    def __call__(self):
        """
        """
#        import pdb;pdb.set_trace()
        return super(MultiLanguages, self).__call__()

class FixedLanguage(BrowserView):
    """
    """

    def __init__(self, context, request):
        """
        """
        self.context = context
        self.request = request
        self.languages = []

    def __call__(self):
        """
        """
