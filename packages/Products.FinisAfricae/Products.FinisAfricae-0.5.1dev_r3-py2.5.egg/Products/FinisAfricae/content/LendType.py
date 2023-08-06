"""



"""
__author__  = 'Juan Grigera <juan@grigera.com.ar>'
__docformat__ = 'restructuredtext'

from types import ListType
from types import TupleType
from types import StringType

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
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget

from Products.ATContentTypes.content.base import ATCTFolder
from Products.ATContentTypes.config import TOOLNAME as ATTOPICS_TOOLNAME

from Products.FinisAfricae.permissions import ChangeLendTypes
from Products.FinisAfricae.config import *
from Products.FinisAfricae.util import updateActions

LendTypeSchema = BaseSchema.copy() 
#LendTypeSchema['id'].validators = ('isValidId',)
LendTypeSchema['id'].searchable = True
LendTypeSchema['description'].schemata = 'default'



class LendType(ATCTFolder):
    """A query for defining if a lend is allowed or not"""

    schema         =  LendTypeSchema

    content_icon   = 'topic_icon.gif'
    portal_type    = meta_type = 'LendType'
    archetype_name = 'Lend Type'
    security       = ClassSecurityInfo()
    immediate_view = default_view  = 'lendtype_view'
    typeDescription= 'A query for defining if a lend is allowed or not'
    typeDescMsgId  = 'description_edit_lendtype'
    filter_content_types  = 1
    allowed_content_types = ()
    __implements__ = ATCTFolder.__implements__

    actions = updateActions(ATCTFolder,
        (
        {
        'id'          : 'conditions',
        'name'        : 'Conditions',
        'action'      : 'string:${object_url}/lendtype_conditions_edit_form',
        'permissions' : (ChangeLendTypes,)
        },
       )
    )




    security.declareProtected(ChangeLendTypes, 'listAvailableConditions')
    def listAvailableConditions(self):
        """Return a list of available conditions for new criteria.
        """
        tool = getToolByName(self, TOOL_NAME)
        return tool.getEnabledConditionsDesc()

    security.declareProtected(View, 'listConditions')
    def listConditions(self):
        """Return a list of our conditions objects.
        """
        #TODO: fix this one val = self.objectValues(self.listConditionMetaTypes())
        val = self.objectValues()
        return val

    security.declareProtected(View, 'listCriteriaTypes')
    def listConditionMetaTypes(self):
	""" Return meta_typesof conditions
	"""
        tool = getToolByName(self, TOOL_NAME)
	return tool.listConditionTypes()
    
    security.declareProtected(ChangeLendTypes, 'addCondition')
    def addCondition(self, condition_type):
        """Add a new condition. Return the resulting object.
        """
        tool = getToolByName(self, TOOL_NAME)
	newid = self.generateUniqueId(type_name=condition_type)
        ct    = tool.getConditionTypeByName(condition_type)
        crit  = ct(newid)

        self._setObject( newid, crit )
        return self._getOb( newid )

    security.declareProtected(ChangeLendTypes, 'deleteCondition')
    def deleteCondition(self, condition_id):
        """Delete selected condition
        """
        if type(condition_id) is StringType:	# single item
            self._delObject(condition_id)
        elif type(condition_id) in (ListType, TupleType):
            for cid in condition_id:
                self._delObject(cid)


    security.declarePublic('getConditionUniqueWidgetAttr')
    def getConditionUniqueWidgetAttr(self, attr):
        """Get a unique list values for a specific attribute for all widgets
           on all conditions"""
        conditions = self.listConditions()
        order = []
        for cond in conditions:
            fields = cond.Schema().fields()
            for f in fields:
                widget = f.widget
                helper = getattr(widget, attr, None)
                # We expect the attribute value to be a iterable.
                if helper:
                    [order.append(item) for item in helper
                        if item not in order]
        return order




    security.declareProtected(View, 'allowedCriteriaForCondition')
    def allowedCriteriaForCondition(self, condition, display_list=False):
        """ Return all valid criteria for a given condition.  Optionally include
            descriptions in list in format [(desc1, val1) , (desc2, val2)] for
            javascript selector."""
#        tool = getToolByName(self, ATTOPICS_TOOLNAME)
#        criteria = tool.getIndex(field).criteria
	allowed = ('criterio1', 'criterio2')
#        allowed = [crit for crit in criteria
#                                if self.validateAddCriterion(field, crit)]
        if display_list:
            flat = []
            for a in allowed:
#                desc = _criterionRegistry[a].shortDesc
                flat.append((a,'descripcion hermosa'))
            allowed = DisplayList(flat)
        return allowed


    # vocabulary
    def getObjectTypes(self):
	"""
	"""	
	tool = getToolByName(self,TOOL_NAME)
	return tool.getLendableObjectTypes()

    def getUserTypes(self):
	"""
	"""	
	tool = getToolByName(self,TOOL_NAME)
	return tool.getAvailableUserTypes()





#    suppl_views    = ('folder_listing', 'folder_summary_view', 'folder_tabular_view', 'atct_album_view')
    use_folder_tabs = 0


    security.declareProtected(ChangeLendTypes, 'validateAddCriterion')
    def validateAddCriterion(self, indexId, criteriaType):
        """Is criteriaType acceptable criteria for indexId
        """
        return criteriaType in self.criteriaByIndexId(indexId)

    security.declareProtected(ChangeLendTypes, 'criteriaByIndexId')
    def criteriaByIndexId(self, indexId):
        catalog_tool = getToolByName(self, CatalogTool.id)
        indexObj = catalog_tool.Indexes[indexId]
        results = _criterionRegistry.criteriaByIndex(indexObj.meta_type)
        return results

    security.declareProtected(ChangeLendTypes, 'listCriteriaTypes')
    def listCriteriaTypes(self):
        """List available criteria types as dict
        """
        return [ {'name': ctype,
                  'description':_criterionRegistry[ctype].shortDesc}
                 for ctype in self.listCriteriaMetaTypes() ]

    security.declareProtected(ChangeLendTypes, 'listSearchCriteriaMetaTypes')
    def listSearchCriteriaMetaTypes(self):
        """List available search criteria
        """
        val = _criterionRegistry.listSearchTypes()
        val.sort()
        return val



    security.declareProtected(ChangeLendTypes, 'setSortCriterion')
    def setSortCriterion( self, field, reversed):
        """Set the Sort criterion.
        """
        self.removeSortCriterion()
        self.addCriterion(field, 'ATSortCriterion')
        self.getSortCriterion().setReversed(reversed)

    security.declareProtected(ChangeLendTypes, 'listIndicesByCriterion')
    def listIndicesByCriterion(self, criterion):
        """
        """
        return _criterionRegistry.indicesByCriterion(criterion)


    security.declareProtected(ChangeLendTypes, 'listSortFields')
    def listSortFields(self):
        """Return a list of available fields for sorting."""
        fields = [ field
                    for field in self.listFields()
                    if self.validateAddCriterion(field[0], 'ATSortCriterion') ]
        return fields

    security.declareProtected(View, 'listSubtopics')
    def listSubtopics(self):
        """Return a list of our subtopics.
        """
        val = self.objectValues(self.meta_type)
        check_p = getToolByName(self.portal_membership).checkPermission
        tops = []
        for top in val:
            if check_p('View', top):
                tops.append((top.getTitle().lower(),top))
        tops.sort()
        tops = [t[1] for t in tops]
        return val

    security.declareProtected(View, 'hasSubtopics')
    def hasSubtopics(self):
        """Returns true if subtopics have been created on this topic.
        """
        val = self.objectIds(self.meta_type)
        return not not val

    security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog.
        """
        tool = getToolByName(self, ATTOPICS_TOOLNAME)
        return tool.getMetadataDisplay(exclude)

    security.declareProtected(View, 'buildQuery')
    def buildQuery(self):
        """Construct a catalog query using our criterion objects.
        """
        result = {}
        return result


    security.declareProtected(View, 'getCriterion')
    def getCriterion(self, criterion_id):
        """Get the criterion object.
        """
        try:
            return self._getOb('crit__%s' % criterion_id)
        except AttributeError:
            return self._getOb(criterion_id)

    security.declarePrivate('synContentValues')
    def synContentValues(self):
        """Getter for syndacation support
        """
        syn_tool = getToolByName(self, 'portal_syndication')
        limit = int(syn_tool.getMaxItems(self))
        brains = self.queryCatalog(sort_limit=limit)[:limit]
        objs = [brain.getObject() for brain in brains]
        return [obj for obj in objs if obj is not None]

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        """
        Override BrowserDefaultMixin because default page stuff doesn't make
        sense for topics.
        """
        return False


    # Beware hack ahead
    security.declarePublic('displayContentsTab')
    def displayContentsTab(self, *args, **kwargs):
        """Only display a contents tab when we are the default page
           because we have our own"""
        putils = getToolByName(self, 'plone_utils', None)
        if putils is not None:
            if putils.isDefaultPage(self):
                script = putils.displayContentsTab.__of__(self)
                return script()
        return False


registerType(LendType, PROJECT_NAME)

