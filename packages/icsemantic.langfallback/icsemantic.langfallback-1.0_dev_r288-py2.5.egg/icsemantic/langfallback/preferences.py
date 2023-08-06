# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: preferences.py 260 2008-06-12 19:53:43Z jpgimenez $
#
# end: Platecom header
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty
from zope.component import queryUtility

from icsemantic.core.annotations import KeywordBasedAnnotations
from icsemantic.core.fieldproperty import AuthenticatedMemberFieldProperty
from icsemantic.langfallback import interfaces

class ManagementUserLanguagesFactory(KeywordBasedAnnotations):
    implements(interfaces.IManageUserLanguages)

    icsemantic_languages = AuthenticatedMemberFieldProperty(interfaces.IManageUserLanguages['icsemantic_languages'],
                                                          'icsemantic.language')
