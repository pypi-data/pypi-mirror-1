# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: events.py 243 2008-06-11 19:45:26Z crocha $
#
# end: Platecom header
"""
icsemantic.langfallback events

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

from zope.component import getUtility

from icsemantic.core.interfaces import IicSemanticManagementContentTypes, \
                                      IContentTypesMultilingualPatcher

def site_patcher(event):
    """
        handler que se dispara en el IBeforeTraverseEvent

        En el event.object recibe el portal y tiene que patchear
        a todos los ContentTypes que esten configurados

            >>> from icsemantic.langfallback.events import site_patcher

            >>> class Event: pass
            >>> event = Event()

        le paso cualquier porqueria como portal...
            >>> event.object = 'portal'
            >>> site_patcher(event)

        le paso un portal pero no es Site...
            >>> event.object = portal
            >>> site_patcher(event)

        le paso un portal que es un Site...
            >>> from zope.app.component.hooks import setSite
            >>> setSite(portal)
            >>> site_patcher(event)

    """
    if not getattr(event.object, '_v_multiligual_patched', None):
        # one time event...
        try:
            pcm=getUtility(IicSemanticManagementContentTypes,
                           name='icsemantic.configuration')
        except:
            # si no tenemos la utility no hacemo'na
            return
        ccpatcher = getUtility(IContentTypesMultilingualPatcher)
        for type_name in pcm.fallback_types:
            try:
                ccpatcher.patch(type_name, True)
                event.object._v_multiligual_patched = True
            except:
                # TODO: reportar el problema de alguna manera
                pass
