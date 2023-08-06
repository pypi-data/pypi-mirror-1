#
#
# 
# Juan Grigera

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Acquisition import aq_parent
from Acquisition import aq_inner
from zExceptions import NotFound

from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import InAndOutWidget
from Products.Archetypes.public import DisplayList

from Products.FinisAfricae.interfaces.FinisAfricaeLendableObject import IFinisAfricaeLendableObject
from Products.FinisAfricae.config import *


class LendableObject(BaseContent):
    """A lendable Object"""
    security = ClassSecurityInfo()
    meta_type      = 'LendableObject'
    portal_type    = 'LendableObject'
    archetype_name = 'Lendable Object'
    __implements__ = IFinisAfricaeLendableObject
#    actions        = updateActions(PloneExFile, ACFilterActions)
  

registerType(LendableObject, PROJECT_NAME)

