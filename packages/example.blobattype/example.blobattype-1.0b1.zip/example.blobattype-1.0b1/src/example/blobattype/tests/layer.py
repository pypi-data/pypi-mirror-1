from Testing.ZopeTestCase import app, close, installPackage
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import PloneSite
from transaction import commit


class Layer(PloneSite):
    """ layer for integration tests """

    @classmethod
    def setUp(cls):
        # load zcml & install packages
        fiveconfigure.debug_mode = True
        from example import blobattype
        zcml.load_config('configure.zcml', blobattype)
        fiveconfigure.debug_mode = False
        installPackage('example.blobattype', quiet=True)
        # import the default profile
        root = app()
        portal = root.plone
        tool = getToolByName(portal, 'portal_setup')
        profile = 'profile-example.blobattype:default'
        tool.runAllImportStepsFromProfile(profile, purge_old=False)
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass
