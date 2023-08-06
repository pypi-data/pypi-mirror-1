# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: admin.py 260 2008-06-12 19:53:43Z jpgimenez $
#
# end: Platecom header
"""
admin setting and preferences
Solo vistas y forms

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import os
from datetime import datetime

import zope
from zope import component
from zope.component import getUtility
from zope.formlib import form
from zope.app.form.browser import MultiSelectSetWidget
from zope.app.form.browser.itemswidgets import MultiSelectWidget \
        as BaseMultiSelectWidget
try:
    from zope.lifecycleevent import ObjectModifiedEvent
except:
    from zope.app.event.objectevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from icsemantic.langfallback import interfaces
from icsemantic.core import pkg_home
from icsemantic.core.i18n import _
from icsemantic.core.browser.base import BaseSettingsForm
from icsemantic.core.browser.widgets import OrderedMultiSelectionWidgetFactory, \
                                           MultiSelectionWidgetFactory

class ManageUserLanguages( BaseSettingsForm ):
    """ Configlet para configurar los lenguajes por usuario
    """
    form_name = _(u'My Languages')
    form_fields = form.Fields( interfaces.IManageUserLanguages )
    form_fields['icsemantic_languages'].custom_widget = OrderedMultiSelectionWidgetFactory
