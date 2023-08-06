# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: utils.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
import sys
from types import FunctionType as function

from Products.Archetypes.utils import capitalize
from Products.ATContentTypes.interfaces import IATContentType
from Products.CMFCore.utils import getToolByName
