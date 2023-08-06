

# Zope
from AccessControl import ClassSecurityInfo

# CMF and Plone
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

# Archetypes, ATSchemaEditorNG
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from XMLArchetype import XMLArchetype, XMLArchetypeSchema

# XML
from lxml import etree 

# FinisAfricae
from Products.FinisAfricae.util import updateActions

# Validators
from Products.validation import V_REQUIRED
from Products.validation.config import validation
from Products.FinisAfricae import validators

validation.register(validators.xmlSchemaValidator('isWellFormedMods', xsd='modsv3.xsd', errmsg = 'Los datos no son un registro MODS v&aacute;lido'))





CatalogObjectModsSchema = ATFolderSchema + XMLArchetypeSchema + Schema ((
    LinesField("isisData",
        searchable = 0,
        required = False,
        mode = 'r',
        widget = LinesWidget(
                label = "ISIS data",
                label_msgid = "label_email",
                description = "ISIS data",
                description_msgid = "help_email",
        )
    ),
))


class CatalogObjectMods(ATFolder, XMLArchetype):
    """
    Catalog Object with Mods Data
    """
    schema         =  CatalogObjectModsSchema
    content_icon   = 'folder_icon.gif'
    portal_type = meta_type = 'CatalogObjectMods'
    archetype_name = 'Catalog: Mods'
    immediate_view = default_view   = 'co_mods_view'
    filter_content_types  = True
    global_allow = 1
    security = ClassSecurityInfo()
    typeDescription= 'A Catalog Object, defined by MODS data.'
#    constrainTypesMode = 1           # 1=local
#    locallyAllowedTypes = immediatelyAddableTypes = allowed_content_types = ( 'LendableObject', )

    # Hide Title from edit
    schema['title'].widget.visible = False
    schema['title'].mode = 'r'
    schema['description'].widget.visible = False
    schema['description'].mode = 'r'
    schema['xmlData'].validators.appendRequired('isWellFormedMods')
    
    _v_dublin_core = None

    actions = updateActions(ATFolder, (
        {
        'id'          : 'fa_mods',
	'name'        : 'MODS',
	'action'      : 'string:${object_url}/r_Mods',
	'permissions' : (View, ),
        'category'    : 'document_actions',
        },
        {
	'id'          : 'fa_dc',
        'name'        : 'Dublin Core',
	'action'      : 'string:${object_url}/r_DublinCore',
	'permissions' : (View, ),
        'category'    : 'document_actions',
	},
        {
        'id'          : 'fa_marcxml',
	'name'        : 'Marc XML',
	'action'      : 'string:${object_url}/r_MarcXml',
	'permissions' : (View, ),
        'category'    : 'document_actions',
        },
    ))
                                                                                                                   

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        self.pretty_print_xmlData()
        self.readDCfromMods()
        
    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        self.pretty_print_xmlData()
        self.setCreators()
        self.readDCfromMods()

    def readDCfromMods(self):
        """
        Reread Dublin Core data from MODS data
        """
        tree = etree.fromstring(self.r_DublinCore(reload=True))
        dc_to_plone = [
           { 'setter': self.setTitle,
             'xpath': '/oai_dc:dc/dc:title',
             'array': False },
           { 'setter': self.setDescription,
             'xpath':  '/oai_dc:dc/dc:description',
             'array': False },
           { 'setter': self.setSubject,
             'xpath':  '/oai_dc:dc/dc:subject',
             'array': True },
           { 'setter': self.setCreators,
             'xpath':  '/oai_dc:dc/dc:creator',
             'array': True },
           { 'setter': self.setContributors,
             'xpath':  '/oai_dc:dc/dc:contributor',
             'array': True },
           { 'setter': self.setLanguage,
             'xpath':  '/oai_dc:dc/dc:language',
             'array': False },
           { 'setter': self.setLocation,
             'xpath':  '/oai_dc:dc/dc:coverage',
             'array': False },
        ]     
 
        for map in dc_to_plone:
            elements = tree.xpath(map['xpath'],
                              namespaces={'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                                          'dc': 'http://purl.org/dc/elements/1.1/'})
            if len(elements):
                if map['array']:
                    texts = [ el.text for el in elements ]
                    map['setter'](texts)
                else:
                    texts = [ el.text for el in elements ]
                    map['setter']( ' '.join(texts) )
                    
                    

                
        self.reindexObject()
        
    #
    #
    # View Helpers
    def getModsAsHtml(self):
        return self.xslTransform(styleSheetName='mods2html.xsl', description='MODS->HTML transform')

    #
    # Helpers
    #
    security.declareProtected(View, 'r_DublinCore')
    def r_DublinCore(self, reload=False):
        """
        returns Dublin Core 
        """
        if self._v_dublin_core is None or reload:
            self._v_dublin_core = self.xslTransform(styleSheetName='MODS3-22simpleDC.xsl', description='MODS->Dublin Core transformation') 
        return self._v_dublin_core 

    security.declareProtected(View, 'r_MarcXml')
    def r_MarcXml(self):
        """
        returns MARC XML 
        """
        return self.xslTransform(styleSheetName='MODS2MARC21slim.xsl', description='MODS->MARCXML transformation')
    
    security.declareProtected(View, 'r_Mods')
    def r_Mods(self):
        """
        returns record formated as MODS
        """
        return self.getXmlData() 

    
    #
    # View helpers
    security.declareProtected(View, 'getShortDetails')
    def getShortDetails(self):
	#TODO: cache this
	#OPTIMIZE: cache this
        return self.xslTransform(styleSheetName='mods2shortdetails.xsl', description='MODS short details extraction')



"""
<dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">Text</dc:type>
<dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">bibliography</dc:type>
<dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">conference publication</dc:type>

<dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Manifestolibri</dc:publisher>

<dc:format xmlns:dc="http://purl.org/dc/elements/1.1/">381 p. ; 21 cm.</dc:format>
<dc:format xmlns:dc="http://purl.org/dc/elements/1.1/">print</dc:format>

<dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">isbn:8872852366</dc:identifier>
<dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">lccn:2001374663</dc:identifier>
"""

        


registerType(CatalogObjectMods)
