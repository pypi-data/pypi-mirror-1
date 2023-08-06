from transaction import savepoint
from Products.CMFCore.utils import getToolByName
try:
    from Products.contentmigration.migrator import BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
except ImportError:
    pass


class ExampleATTypeMigrator(BaseInlineMigrator):
    """ example content migrator """

    src_portal_type = 'ExampleATType'
    src_meta_type = 'ExampleATType'
    dst_portal_type = 'ExampleATType'
    dst_meta_type = 'ExampleATType'

    fields_map = {
        'afile': None,
        'secondfile': None,
    }

    def migrate_data(self):
        f = self.obj.getField('afile').get(self.obj)
        self.obj.getField('afile').getMutator(self.obj)(f)
        f = self.obj.getField('secondfile').get(self.obj)
        self.obj.getField('secondfile').getMutator(self.obj)(f)

    def last_migrate_reindex(self):
        self.obj.reindexObject()


def migrateExampleATTypes(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    migrator = ExampleATTypeMigrator
    walker = CustomQueryWalker(portal, migrator, full_transaction=True)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()
