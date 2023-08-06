from zope import schema
from zope.interface import Interface

from example.blobattype import blobattypeMessageFactory as _


class IExampleATType(Interface):
    """An AT-based content type with FileFields"""

    afile = schema.Bytes(
        title=_(u"A file"),
        required=True,
        description=_(u"Some file"),
    )

    secondfile = schema.Bytes(
        title=_(u"Other file"),
        required=True,
        description=_(u"Some other file"),
    )
