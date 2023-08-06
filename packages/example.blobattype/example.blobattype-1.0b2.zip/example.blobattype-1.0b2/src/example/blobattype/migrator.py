from plone.app.blob.migrations import migrate


def migrateExampleATTypes(context):
    return migrate(context, 'ExampleATType')
