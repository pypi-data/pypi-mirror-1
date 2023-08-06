from Products.PloneTestCase.ptc import setupPloneSite, PloneTestCase
from example.blobattype.tests.layer import Layer


setupPloneSite()


class BlobTestCase(PloneTestCase):
    """ base class for integration tests """

    layer = Layer
