# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: helpers.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName

from icsemantic.core.fieldproperty import ATFieldProperty, \
                                         ATFieldMultilingualProperty

from icsemantic.langfallback import LangviewMessageFactory as _
from icsemantic.langfallback.config import PROJECTNAME

# ATMock schema, campos de archetype para nuestra clase de Mock
ATMockSchema = ATDocument.schema.copy() + atapi.Schema((
    atapi.StringField('textoMultilingue',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Multilingual text"),
                                  description=_(u""),
                                  )
        ),
        ))
finalizeATCTSchema(ATMockSchema)

class ATMock(ATDocument):
    """ Describe a ATMock.
        ATMock es una clase de archetypes para hacer pruebas en los tests.
        No debe cargarse en una instalacion estandar del sistema.
    """

    portal_type = meta_type = archetype_name = 'ATMock'
    _at_rename_after_creation = True
    schema = ATMockSchema
    global_allow = True

    __implements__ = ATDocument.__implements__
    actions = ATDocument.actions

    # FieldProperty accessors, uno prueba el modo comun de hacerlo
    # el otro utiliza accessors multilingues...
    multilingual_text = ATFieldProperty('textoMultilingue')
    multilingual_title = ATFieldMultilingualProperty('title')

registerATCT(ATMock, PROJECTNAME)
