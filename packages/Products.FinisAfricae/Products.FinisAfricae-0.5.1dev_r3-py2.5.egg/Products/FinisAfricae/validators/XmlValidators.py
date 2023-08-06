#
#
#

# System
from lxml import etree        # deb-depends: python-lxml
from StringIO import StringIO

# Validator
from Products.validation.interfaces.IValidator import IValidator

# CMF
from Products.CMFCore.utils import getToolByName

#
# Validators
class xmlSyntaxValidator:
    __implements__ = IValidator
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        f = StringIO(value)

        try:
            doc = etree.parse(f)
        except etree.XMLSyntaxError, e:
            return "XML Syntax Invalid. Error: %s" % e


class xmlSchemaValidator:
    __implements__ = IValidator
    
    def __init__(self, name, *args, **kw):
        self.name = name
        self.xsd = kw.get('xsd', None)
        self.errmsg = kw.get('errmsg', 'fails tests of %s' % name)

    def __call__(self, value, *args, **kwargs):
        self.instance = kwargs.get('instance', None)

        try:
            f = StringIO(value)
            doc = etree.parse(f)
        except etree.XMLSyntaxError, e:
            return "XML Syntax Invalid. Error: %s" % e
        
        # Get Schema
        try:
            xsdSchema = self.restrictedTraverse(self.xsd)._readFile(0)
            xsd_stringio = StringIO(xsdSchema)                     # Compute stringIO
            xsd_doc = etree.parse(xslt_stringio)                   # Parse XSL
            xsd_schema = etree.XMLSchema(xsd_doc)                  # Make it a nice tree
        except AttributeError, e:
            return "INTERNAL ERROR '%s' not found! Schema validation failed! %s" % (self.xsd, str(e))
        except etree.XMLSyntaxError, e:
            return "INTERNAL ERROR '%s' is not valid! Schema validation failed! %s" % (self.xsd, str(e))

        # Validate schema
        if xsd_schema.validate(doc):
            return
        else:
            return "%s\n%s" % (self.errmsg, xsd_schema.error_log)
            
            