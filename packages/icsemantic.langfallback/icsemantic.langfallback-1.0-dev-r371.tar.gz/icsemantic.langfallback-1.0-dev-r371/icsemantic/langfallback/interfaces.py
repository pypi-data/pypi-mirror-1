# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 326 2008-07-15 18:09:25Z crocha $
#
# end: Platecom header
""" icsemantic.langfallback interfaces.
"""
# pylint: disable-msg=W0232,R0903

from zope.interface import Interface
from zope import schema
from icsemantic.core.i18n import _

class IMemberDataTool(Interface):
    """
    Decorate user objects with site-local data.
    First we need some mock class...
        >>> from minimock import Mock
        >>> from icsemantic.langfallback.interfaces import IMemberDataTool

        >>> memberdata = Mock('memberdata')
        >>> memberdata = self.portal.portal_memberdata
        >>> IMemberDataTool.providedBy(memberdata)
        True

    """

class IPartialTranslated(Interface):
    """
    """

class IManageUserLanguages( Interface ):
    """
    """
    icsemantic_languages = schema.List(title = _(u"User Languages"),
                                     required = False,
                                     default = [],
                                     description = _(u"User Languages"),
                                     value_type=schema.Choice(vocabulary="icsemantic.languages"))
