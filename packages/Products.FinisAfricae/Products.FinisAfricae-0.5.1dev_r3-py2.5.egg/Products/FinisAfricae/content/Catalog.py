

# Zope
from AccessControl import ClassSecurityInfo

# CMF and Plone
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

# Archetypes, ATSchemaEditorNG
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder

# FinisAfricae
from Products.FinisAfricae.util import updateActions
from Products.FinisAfricae.AZLinksHelper import AZLinksHelper

class CatalogContainer(ATBTreeFolder):
    """
    Container to hold a catalog, i.e. large number of mods objects
    """
    content_icon   = 'catalogcontainer_icon.png'
    portal_type = meta_type = 'CatalogContainer'
    archetype_name = 'Catalog'
    immediate_view = default_view   = 'catalog_view'
    filter_content_types  = True
    global_allow = 1
    constrainTypesMode = 1           # 1=local
    locallyAllowedTypes = immediatelyAddableTypes = allowed_content_types = ( 'CatalogObjectMods', 'Large Plone Folder',)
    security = ClassSecurityInfo()
    typeDescription= 'A collection of catalog entries..'

    actions = updateActions(ATBTreeFolder,
        ({
        'id'          : 'keywords',
        'name'        : 'Keywords',
        'action'      : 'string:${object_url}/catalog_azkeywords_view',
        'permissions' : (View,)
        },
       )
    )

    catalog_id_counter = 0
    slot_folder_type = 'Large Plone Folder'
    
    def _create_slot(self, base, slot):
        fldid = base.invokeFactory(self.slot_folder_type, '%s' % slot, title = 'slot %s' % slot,
                                           description='Catalog slot container')
        return getattr(base, fldid)
        
    def appendModsObject(self, modsData = None, oldData = None, updateMetadata = True):
        """ 
        Create a new object in the catalog using modsData as Data
        """
        self.catalog_id_counter = self.catalog_id_counter + 1
        slot = int(self.catalog_id_counter / 500)

        # Buscar donde nos toca ponerlo
        try:
            slot_obj = getattr(self, "%s" % slot)
        except AttributeError:
            slot_obj = self._create_slot(self, slot)
        
        modsobjid = slot_obj.invokeFactory('CatalogObjectMods', '%s' % self.catalog_id_counter, 
    				    title = None, description='Catalog object',
                                    xmlData = modsData, isisData = oldData)
        if updateMetadata:
    	    modsobj = getattr(slot_obj, modsobjid)
    	    modsobj.at_post_edit_script()

    #
    def getAZLinksHelper(self, context = None, request = None):
        """
        """
        context = context is not None and context or self
        return AZLinksHelper(context, request)


registerType(CatalogContainer)
