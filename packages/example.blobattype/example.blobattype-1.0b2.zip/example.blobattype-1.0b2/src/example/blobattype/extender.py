from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.field import BlobField

from Products.Archetypes import atapi

from example.blobattype.interfaces import IExampleATType
from example.blobattype import blobattypeMessageFactory as _


class ExtensionBlobField(ExtensionField, BlobField):
    """ derivative of blobfield for extending schemas """


class ExampleATTypeExtender(object):
    adapts(IExampleATType)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField('afile',
            widget=atapi.FileWidget(
                label=_(u"A file"),
                description=_(u"Some file"),
            ),
            required=True,
            validators=('isNonEmptyFile'),
        ),

        ExtensionBlobField('secondfile',
            widget=atapi.FileWidget(
                label=_(u"Some other file"),
                description=_(u"Some other file"),
            ),
            required=True,
            validators=('isNonEmptyFile'),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
