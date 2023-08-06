
# Python imports
from os.path import join
from DateTime import DateTime

# Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain, aq_inner

# CMF and Plone
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.utils import createViewName, classImplements, implementedBy

# Archetypes, ATSchemaEditorNG
from Products.Archetypes.public import *
from Products.ATSchemaEditorNG.ParentManagedSchema import ParentOrToolManagedSchema

# Membrane
from Products.Membrane.interfaces.group import IGroup
from Products.Membrane.interfaces.user import IUser
from Products.Membrane.types.UserMixin import Authentication, Properties, Groups


#
# Schema
# 
LibraryUserSchema = BaseSchema + Schema((
    StringField('userName',
        languageIndependent = 1,
        searchable = 1,
        required = 1,
        widget = StringWidget (
            description = "Username for a person."
        )
    ),
    StringField('password',
        languageIndependent = 1,
        required = 1,
        searchable = 0,
        widget = StringWidget(
            description = "Password."
        )
    ),
    StringField("firstname",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "Firstname",
                label_msgid = "label_firstname",
                description = None,
                description_msgid = "help_firstname",
        ),
    ),
    StringField("surname",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "Surname",
                label_msgid = "label_surname",
                description = None,
                description_msgid = "help_surname",
        ),
    ),
    
#    ComputedField('fullname',
#        default='',
#        schemata = "personal",
 #       accessor='getFullName',
  #      mutator='setFullName',
#        read_permission=VIEW_PUBLIC_PERMISSION,
#        write_permission=EDIT_PROPERTIES_PERMISSION,
  #      widget=StringWidget(
   #         label='Full name',
    #        label_msgid='label_full_name',
     #       description="Enter full name, eg. John Smith.",
      #      description_msgid='help_full_name_creation',
       #     i18n_domain='plone',
        #    visible = {'view' : 'invisible',
         #       'edit' : 'invisible' }
          #  ),
#    ),
    StringField("gender",
        vocabulary = "getGenderList",
        schemata = "personal",
        widget = SelectionWidget(
                format='select', # possible values: flex, select, radio
                label = "Gender",
                label_msgid = "label_gender",
                description = None,
                description_msgid = "help_gender",
                ),
    ),
    StringField("address",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "Address",
                label_msgid = "label_address",
                description = None,
                description_msgid = "help_address",
        ),
    ),
    StringField("city",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "City",
                label_msgid = "label_city",
                description = None,
                description_msgid = "help_city",
            ),
    ),
    StringField("zipcode",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "ZIP",
                label_msgid = "label_zipcode",
                description = None,
                description_msgid = "help_zipcode",
                ),
    ),
    StringField("state",
        searchable = 1,
        required = 1,
        schemata = "personal",
        widget = StringWidget(
                label = "State",
                label_msgid = "label_state",
                description = None,
                description_msgid = "help_state",
        ),
    ),
    StringField("country",
        searchable = 1,
        required = 1,
        schemata = "personal",
        vocabulary = 'getCountryList',
        widget = StringWidget(
                label = "Country",
                label_msgid = "label_country",
                description = None,
                description_msgid = "help_country",
        ),
    ),

    # TODO: Arrray Field de fones+descr
#       StringField("phone",
 #                 searchable = 1,
  #                validators = ("isInternationalPhoneNumber",),
#                  widget = StringWidget(
#                         label = "Dirrect phone",
#                         label_msgid = "label_phone",
#                         description = None,
#                         description_msgid = "help_phone",
#                         ),
#                  ),

    StringField("email",
        searchable = 1,
        schemata = "personal",
        # validators = 
        widget = StringWidget(
                label = "e-Mail",
                label_msgid = "label_email",
                description = None,
                description_msgid = "help_email",
        )
    ),
    
    # extra emails
    # arayfield...
#    
#    DateTimeField("last_change_date",
#        default = DateTime(),
 #       schemata = "personal",
#        index='DateIndex',
#        widget = CalendarWidget(
#                label = "Last Change Date",
#                label_msgid = "label_last_change_date",
#                description = None,
#                description_msgid = "help_last_change_date",
#        ),
#    ),
))


class LibraryUser(ParentOrToolManagedSchema, Authentication, Properties, Groups, BaseContent):
    """ Library User
    """ 
    schema = LibraryUserSchema
    archetype_name = "Library User"
    portal_type = meta_type = 'LibraryUser'
    global_allow = 0
    security = ClassSecurityInfo()
    _at_rename_after_creation = True
    
    #isAnObjectManager = 1
    #isPrincipiaFolderish = 1
    #processForm = Member.processForm
    #update = Member.update
    #getProperty = Member.getProperty

    def getSelectionValues(self, prop_name):
        """make vocabulary out of given property"""
        pp = getToolByName(self, 'portal_properties')
        ip = getattr(pp, 'atcontent_type_properties')
        labels = ip.getProperty(prop_name,[])
        values = list(labels)
        del(values[0])
        values.insert(0,"")
        return DisplayList(zip(values, labels))


    def getCountryList(self):
        """vocabulary of countries """
        labels = ('Argentina', 'Uruguay', )
        values = list(labels)
        return DisplayList(zip(values, labels))
#        return self.getSelectionValues('countries')

    def getGenderList(self):
        """vocabulary of genders"""
        labels = ('Mujer', 'Hombre', )
        values = list(labels)
        return DisplayList(zip(values, labels))
#        return self.getSelectionValues('genders')

    def getSchema(self):
        """override variable schema"""
        return self.schema

    def getPhones(self):
        """generate phones string"""
        phones = []
        if self.getPhone():
           phones.append(self.getPhone())
        if self.getPhone2():
           phones.append(self.getPhone2())
        if self.getMobiel():
           phones.append(self.getMobiel())
        return phones
  
    def getFullName(self):
        """compute the full name"""
        name = []
        if self.getFirstname():
           name.append(self.getFirstname())
        if self.getSurname():
           name.append(self.getSurname())
        res = ' '.join(name)
        return res.lstrip()

    #
    # ATSchemaEditorNG needs to refresh schema
    #
    def manage_afterAdd(self, item, container):
        self.updateSchemaFromEditor()
        BaseContent.manage_afterAdd(self, item, container)


    #
    # For IAuthenticationPlugin implementation/Authentication mixin
    # - should define this as an interface
    #
    # getUserName is autogenerated
    #
    def _getPassword(self):
        return self.Schema()['password'].get(self)

    def getUserId(self):
        return self.UID()

    def getUserName(self):
        return self.getFullName()
    
    #
    # For IPropertiesPlugin implementation/Property mixin
    # - should probably use an interface
    #
    security.declarePrivate( 'getUserPropertySchematas' )
    def getUserPropertySchemata(self):
        return ['userinfo']

    #
    # For IGroupsPlugin implementation/Group mixin
    # - should probably use an interface
    #
    security.declarePrivate( 'getGroupRelationships' )
    def getGroupRelationships(self):
        return ['participatesInProject']


classImplements( LibraryUser
               , *tuple(implementedBy(LibraryUser)) +
                 (IUser,)) # Insert extra interfaces in empty tuple

registerType(LibraryUser)
