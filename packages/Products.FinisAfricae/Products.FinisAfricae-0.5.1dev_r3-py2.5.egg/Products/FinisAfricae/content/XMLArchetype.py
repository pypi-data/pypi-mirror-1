

# Zope
from AccessControl import ClassSecurityInfo

# CMF and Plone
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

# Archetypes, ATSchemaEditorNG
from Products.Archetypes.public import *

# Validators
from Products.validation import V_REQUIRED
from Products.validation.config import validation
from Products.FinisAfricae import validators

# XML
from StringIO import StringIO
from lxml import etree 



XMLArchetypeSchema = Schema ((
    TextField("xmlData",
        validators = (('isValidXmlSyntax', V_REQUIRED),),
        required = True,
        widget = TextAreaWidget(
                rows = 45,
                label = "XML data",
                label_msgid = "label_email",
                description = "Enter raw XML data here",
                description_msgid = "help_email",
        )
    ),
))


class XMLArchetype:
    """

    """
    # TODO: Caching! some XSL data can be cached
    # XSLT objects cant be pickled, thus must begin with _v_
    _v_xslt_cache = {}
    
    def pretty_print_xmlData(self):
        """
        
        reformat XML data pretty printing them
        """
        xmlField = self.getField('xmlData')
        f = StringIO(xmlField.getRaw(self))
        tree = etree.parse(f, etree.XMLParser(remove_blank_text=True))
        self.setXmlData(etree.tostring(tree.getroot(), pretty_print=True))
        
    def getXmlTree(self):
	"""
	
	"""
	xmlField = self.getField('xmlData')
        f = StringIO(xmlField.getRaw(self))
        return etree.parse(f)
    
    def getXslT(self, styleSheet):
        """
        compiles XSL contained in 'styleSheet'
        saves compiled XSLTs with simple caching scheme
        
        returns XSLT
        """
        if self._v_xslt_cache is None:
            self._v_xslt_cache = {}
            
        styleSheetHash = hash(styleSheet) 
        try:
            xslt_transform = self._v_xslt_cache[styleSheetHash]        
        except KeyError:    # Item not there
            xslt_stringio = StringIO(styleSheet)                    # Compute stringIO
            xslt_doc = etree.parse(xslt_stringio)                   # Parse XSL
            xslt_transform = etree.XSLT(xslt_doc)                   # Make it a nice tree
            self._v_xslt_cache[styleSheetHash] = xslt_transform     # Save for future use
            
        return xslt_transform

    def xslTransform(self, styleSheet=None, styleSheetName=None, description='XML->HTML transformation'):
        """
        styleSheet: string containing style sheet or
        styleSheetName: name of resource that contains it
        
        either styleSheet or styleSheetName should not be None

        returns HTML formatted error or XSL result
        """
        if styleSheet is None:
            try:
                styleSheet = self.restrictedTraverse(styleSheetName)._readFile(0)
            except AttributeError, e:
                return self.formatHtmlError('INTERNAL ERROR', "'%s' not found! %s failed!" % (styleSheetName, description), e)

        # Get XSL Transformation
        try:
            xslT = self.getXslT(styleSheet)
        except etree.XMLSyntaxError, e:
            return self.formatHtmlError('INTERNAL ERROR', "%s failed, styleSheet has errors!" % description, e)

        # Get Raw Data
        xmlField = self.getField('xmlData')
        f = StringIO(xmlField.getRaw(self))
        
        # Apply XSL to XML in field
        try:
            doc = etree.parse(f)
            html_data = str( xslT(doc) )
        except etree.XMLSyntaxError, e:
            return self.formatHtmlError('ERROR', "XML Data is not valid, when doing %s!" % description, e)
            
        return html_data
           
        pass

    def formatHtmlError(self, error_type, description, e):
        return '<div><b>%s:</b> %s<br/>%s</div>' % (error_type, description, str(e))

    
