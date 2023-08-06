from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from example.blobattype import blobattypeMessageFactory as _
from example.blobattype.interfaces import IExampleATType
from example.blobattype.config import PROJECTNAME


ExampleATTypeSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.FileField(
        'afile',
        widget=atapi.FileWidget(
            label=_(u"A file"),
            description=_(u"Some file"),
        ),
        required=True,
        validators=('isNonEmptyFile'),
    ),

    atapi.FileField(
        'secondfile',
        widget=atapi.FileWidget(
            label=_(u"Some other file"),
            description=_(u"Some other file"),
        ),
        required=True,
        validators=('isNonEmptyFile'),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

schemata.finalizeATCTSchema(ExampleATTypeSchema, moveDiscussion=False)


class ExampleATType(base.ATCTContent):
    """An AT-based content type with FileFields"""
    implements(IExampleATType)

    meta_type = "ExampleATType"
    schema = ExampleATTypeSchema


atapi.registerType(ExampleATType, PROJECTNAME)
