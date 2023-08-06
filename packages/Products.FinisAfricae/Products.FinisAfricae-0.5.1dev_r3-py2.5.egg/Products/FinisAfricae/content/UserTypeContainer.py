

# Zope
from AccessControl import ClassSecurityInfo

# CMF and Plone
from Products.CMFCore.utils import getToolByName

# Archetypes, ATSchemaEditorNG
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATSchemaEditorNG.SchemaEditor import SchemaEditor

from Products.FinisAfricae.util import updateActions
from Products.FinisAfricae.content.LibraryUser import LibraryUser


class UserTypeContainer(SchemaEditor, ATFolder):
    """
    Container to hold a type of users.
    """
#    schema         =  ATFolderSchema
    
    content_icon   = 'folder_icon.gif'
    portal_type = meta_type = 'UserTypeContainer'
    archetype_name = 'User Type'
    immediate_view = default_view   = 'usertype_view'
    filter_content_types  = True
    global_allow = 1
    constrainTypesMode = 1           # 1=local
    locallyAllowedTypes = immediatelyAddableTypes = allowed_content_types = ( 'LibraryUser', )
    security = ClassSecurityInfo()
    typeDescription= 'A collection of users of the same type.'
    typeDescMsgId  = 'description_usertype_folder'

    actions = updateActions(ATFolder,
        ({'id': 'editor_view',
            'name': 'Schema Editor',
            'action': 'string:${object_url}/atse_editor',
            'permissions': ('Manage portal',)
           },
          {'id': 'import_export_members',
            'name': 'Import/Export',
            'action': 'string:users_import_export',
            'permissions': ('Manage portal',),
            },)
    )


    def manage_afterAdd(self, item, container):
        """ """
        # do not show metadata fieldset
        self.atse_registerObject( LibraryUser, ('metadata', ))
        ATFolder.manage_afterAdd(self, item, container)
	
    def getAddLabel(self):
	return "Agregar " + self.Title()


registerType(UserTypeContainer)
