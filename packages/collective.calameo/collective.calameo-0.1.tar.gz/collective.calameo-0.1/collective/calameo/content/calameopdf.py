"""Definition of the Calameo PDF content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import document


from collective.calameo import calameoMessageFactory as _
from collective.calameo.interfaces import ICalameoPDF
from collective.calameo.config import PROJECTNAME

CalameoPDFSchema = document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'calameoid',
        storage=atapi.AnnotationStorage(),
        accessor = "calemeoId",

        widget=atapi.StringWidget(
            label=_(u"Calameo Id"),
            description=_(u"Insert the ID of Calameo publication"),
        ),
        required=True,
    ),


    atapi.IntegerField(
        'width',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Width"),
            description=_(u"Insert the width of Calameo Flash applet in pixel"),
        ),
        default=_(u"520"),
        validators=('isInt'),
    ),


    atapi.IntegerField(
        'height',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Height"),
            description=_(u"Insert the height of Calameo Flash applet in pixel"),
        ),
        required=True,
        default=_(u"380"),
        validators=('isInt'),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

CalameoPDFSchema['title'].storage = atapi.AnnotationStorage()
CalameoPDFSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(CalameoPDFSchema, moveDiscussion=False)

class CalameoPDF(document.ATDocumentBase):
    """Calameo publication in Plone"""
    implements(ICalameoPDF)

    meta_type = "CalameoPDF"
    schema = CalameoPDFSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    calameoid = atapi.ATFieldProperty('calameoid')

    width = atapi.ATFieldProperty('width')

    height = atapi.ATFieldProperty('height')

    def calemeoId(self):
        return self.calameoid

atapi.registerType(CalameoPDF, PROJECTNAME)
