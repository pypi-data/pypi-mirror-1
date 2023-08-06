# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: propertiestool.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Plone Properties tool setup handlers.
"""

from Products.CMFPlone.exportimport.propertiestool import \
        SimpleItemWithPropertiesXMLAdapter as \
        BaseAdapter

class SimpleItemWithPropertiesXMLAdapter(BaseAdapter):

    """Node im- and exporter for SimpleItemWithProperties.
    """
    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        obj = self.context
        self._initProperties(node)
        properties = [child for child in node.childNodes \
                      if child.nodeName == 'property']
        for property in properties:
            if property.getAttribute('remove') == 'True':
                obj._delProperty(property.getAttribute('name'))
