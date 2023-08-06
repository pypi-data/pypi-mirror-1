#
#
# Import and register validators

from Products.validation.config import validation

from XmlValidators import xmlSchemaValidator
from XmlValidators import xmlSyntaxValidator

validation.register(xmlSyntaxValidator('isValidXmlSyntax'))
