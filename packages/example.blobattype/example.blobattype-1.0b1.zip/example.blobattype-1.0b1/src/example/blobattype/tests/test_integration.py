from unittest import defaultTestLoader
from zope.component import getGlobalSiteManager
from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.interfaces import IBlobWrapper
from plone.app.blob.tests.utils import getFile
from example.blobattype.interfaces import IExampleATType
from example.blobattype.extender import ExampleATTypeExtender
from example.blobattype.migrator import migrateExampleATTypes
from example.blobattype.tests.base import BlobTestCase


def makeUnmigratedInstance(container, *args, **kw):
    """ create an instance using the old FileFields;  to do so the
        the schemaextender gets temporarily unregistered """
    gsm = getGlobalSiteManager()
    gsm.unregisterAdapter(factory=ExampleATTypeExtender,
        required=[IExampleATType], provided=ISchemaExtender)
    obj = container[container.invokeFactory('ExampleATType', *args, **kw)]
    # re-register the schemaextender
    gsm.registerAdapter(factory=ExampleATTypeExtender,
        required=[IExampleATType], provided=ISchemaExtender)
    return obj


class FileReplacementTests(BlobTestCase):

    def testCreateInstance(self):
        foo = self.folder[self.folder.invokeFactory('ExampleATType', 'foo')]
        self.failUnless(IBlobWrapper.providedBy(foo.getAfile()), 'no blob?')

    def testCreateUnmigratedInstance(self):
        foo = makeUnmigratedInstance(self.folder, 'foo', title='Foo')
        self.failIf(IBlobWrapper.providedBy(foo.getAfile()), 'blob?')

    def testMigration(self):
        foo = makeUnmigratedInstance(self.folder, 'foo', title='Foo',
            afile='plain text', secondfile=getFile('plone.pdf'),
            subject=('foo', 'bar'), contributors=('me'))
        # check to be migrated content
        self.failIf(IBlobWrapper.providedBy(foo.getAfile()), 'blob?')
        self.failIf(IBlobWrapper.providedBy(foo.getSecondfile()), 'blob?')
        self.assertEqual(foo.Title(), 'Foo')
        self.assertEqual(foo.getAfile().getContentType(), 'text/plain')
        self.assertEqual(foo.getSecondfile().getContentType(), 'application/pdf')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        # migrate & check migrated content item
        self.assertEqual(migrateExampleATTypes(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (ExampleATType -> ExampleATType)\n')
        foo = self.folder['foo']
        self.failUnless(IBlobWrapper.providedBy(foo.getAfile()), 'blob?')
        self.failUnless(IBlobWrapper.providedBy(foo.getSecondfile()), 'blob?')
        self.assertEqual(foo.Title(), 'Foo')
        self.assertEqual(foo.getAfile().getContentType(), 'text/plain')
        self.assertEqual(foo.getSecondfile().getContentType(), 'application/pdf')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        afile = foo.getAfile().getBlob().open('r')
        self.assertEqual(afile.read(), 'plain text')
        secondfile = foo.getSecondfile().getBlob().open('r')
        self.assertEqual(secondfile.read(), getFile('plone.pdf').read())


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
