# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: vocabularies.py 267 2008-06-13 18:32:24Z flarumbe $
#
# end: Platecom header
"""
"""
from zope.schema import vocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.component import getUtility
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.utils import safe_unicode

from icsemantic.core.i18n import _
from icsemantic.core.config import HAS_PLONE3

import cgi

if HAS_PLONE3:
    from plone.i18n.locales.interfaces import IContentLanguageAvailability
else:
    from Products.PloneLanguageTool import availablelanguages

from iccommunity.mailman.interfaces import IicCommunityManagementMailman, IicCommunityMailman

class AvailableLanguagesVocabulary(object):
    """

    Test ContentTypes vocab,

        >>> from iccommunity.mailman.vocabularies import MailmanploneListsVocabulary
        >>> vocab = MailmanploneListsVocabulary(portal)
        >>> vocab
        <zope.schema.vocabulary.SimpleVocabulary object at ...>

    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)

        portal_languages = getToolByName(context, 'portal_languages')
        terms = portal_languages.listSupportedLanguages()

        return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(term[0], title=safe_unicode(term[1])) \
                                            for term in terms])

AvailableLanguagesVocabularyFactory = AvailableLanguagesVocabulary()
