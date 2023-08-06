from Products.ATContentTypes.content import  schemata
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.ATContentTypes.content import file
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema

#from Products.ATContentTypes.content.document import ATDocument
#from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.Archetypes import atapi
from Products.Archetypes.atapi import BaseSchema

from Products.Archetypes.Schema import Schema
from Products.Archetypes.atapi import StringField,TextField
from Products.Archetypes.atapi import TextAreaWidget, SelectionWidget
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT

# Tesseract supported languages
langs = [('default','-- Site default --'),
         ('de','Deutsch'), ('en','English'), ( 'fr','Français'),
         ('it','Italiano'), ('nl','Nederlands'),('po','Português')]

extra_schema = Schema((
        TextField(
            name='textFromOcr',
            widget=TextAreaWidget(
                label="Text from OCR",
                description="Text from PDF documents using OCR",
                visible = {"edit": "invisible", "view": "invisible"},
            ),
            searchable=1,
        ),
        StringField('docLanguage',
            vocabulary = langs,
            default = 'default',
            widget=SelectionWidget(
                label="Language", 
                description="Language is used for ocr processing a pdf document",
                format='select')
            ),
))


if not ATFileSchema.has_key('textFromOcr'):
    ATFile.schema = ATFile.schema + extra_schema.copy()

registerATCT(ATFile, PROJECTNAME)

print "patched ATContentTypeSchema (ocr and language fields added to ATFile)"

