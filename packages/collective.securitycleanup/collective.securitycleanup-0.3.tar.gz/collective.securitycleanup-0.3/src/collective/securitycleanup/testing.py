import time

import Acquisition
from Testing import ZopeTestCase
from Products.CMFTestCase import ctc
from Products.CMFTestCase import layer
from Products.CMFTestCase import setup

from Products.CMFDefault import factory

from collective.testcaselayer import ctc as tcl_ctc

class SiteSetup(setup.SiteSetup):

    def _app(self):
        """Set up the portal container first"""
        app = setup.SiteSetup._app(self)
        if 'folder' not in app.objectIds():
            app.manage_addFolder('folder')
        return app.folder

    def _close(self):
        '''Closes the ZODB connection.'''
        ZopeTestCase.close(Acquisition.aq_parent(self.app))

    def _setupCMFSite_with_genericsetup(self):
        '''Creates the site using GenericSetup.'''
        start = time.time()
        if self.base_profile != setup.default_base_profile:
            self._print('Adding CMF Site (%s) ... ' %
                        (self.base_profile,))
        else:
            self._print('Adding CMF Site ... ')
        factory.addConfiguredSite(
            getattr(self.app, 'folder'),
            self.id, snapshot=0, profile_id=self.base_profile)
        self._commit()
        self._print('done (%.3fs)\n' % (time.time()-start,))

class ContainedPortal(object):

    def getPortal(self):
        """Return the portal from our custom location"""
        return getattr(self.app.folder, ctc.portal_name)

class InstallLayer(ContainedPortal, tcl_ctc.BaseCTCLayer):

    def setUp(self):
        """Use customized SiteSetup to setup the site"""
        try:
            SiteSetup(
                id=ctc.portal_name, products=setup.default_products,
                quiet=0, base_profile=setup.default_base_profile,
                extension_profiles=setup.default_extension_profiles).run()
            super(InstallLayer, self).setUp()
        except:
            import sys, pdb
            exc_info = sys.exc_info()
            pdb.post_mortem(exc_info[2])
            self._clear()
            raise

    def afterSetUp(self):

        self.app.manage_permission(
            'Modify portal content', ['Authenticated', 'Manager'])
        self.app.manage_addLocalRoles('test_user_1_', ('Owner',))

        self.app.folder.manage_permission(
            'Add portal content', ['Authenticated', 'Manager'])
        self.app.folder.manage_addLocalRoles(
            'test_user_1_', ('Manager',))

        self.portal.manage_permission(
            'Review portal content', ['Owner', 'Manager'])
        self.portal.manage_addLocalRoles(
            'test_user_1_', ('Member',))

        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='folder', type_name='Folder')
        self.portal.folder.invokeFactory(
            id='document', type_name='Document')
        self.logout()

        self.portal.folder.manage_permission(
            'Add portal folders', ['Manager', 'Reviewer'])
        self.portal.folder.manage_addLocalRoles(
            'test_user_1_', ('Reviewer',))

        self.portal.folder.document.manage_permission(
            'Copy or Move', ['Manager', 'Member'])
        self.portal.folder.document.manage_addLocalRoles(
            'test_user_1_', ('Owner',))
        self.portal.folder.document.setCreators(('test_user_1_',))
        
class FunctionalTestCase(ContainedPortal, ctc.FunctionalTestCase):
    pass
        
install_layer = InstallLayer([layer.ZCML])
    
