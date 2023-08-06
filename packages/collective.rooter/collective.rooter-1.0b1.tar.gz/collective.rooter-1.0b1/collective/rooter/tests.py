import unittest

from zope.interface import alsoProvides
from zope.event import notify
from zope.app.publication.interfaces import BeforeTraverseEvent
from Products.CMFCore.utils import getToolByName

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from plone.app.layout.navigation.interfaces import INavigationRoot

from collective.rooter import getNavigationRoot

@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import collective.rooter
    zcml.load_config('configure.zcml', collective.rooter)
    fiveconfigure.debug_mode = False
    
setup_package()
ptc.setupPloneSite()

class IntegrationTests(ptc.PloneTestCase):
    
    
    def test_search_root(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'site1')
        alsoProvides(self.portal.site1, INavigationRoot)
        
        self.portal.invokeFactory('Document', 'd1')
        self.portal.site1.invokeFactory('Document', 'd2')

        catalog = getToolByName(self.portal, 'portal_catalog')

        lazy = catalog(portal_type='Document')
        results = [x.getId for x in lazy]
        self.failUnless('d1' in results)
        self.failUnless('d2' in results)

        # Simulate traversal
        notify(BeforeTraverseEvent(self.portal.site1, self.portal.REQUEST))
        
        root = getNavigationRoot()
        self.assertEquals(root.absolute_url(), self.portal.site1.absolute_url())
        
        lazy = catalog(portal_type='Document')
        results = [x.getId for x in lazy]
        self.failIf('d1' in results)
        self.failUnless('d2' in results)
    
    def test_search_root_with_explicit_path(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'site1')
        alsoProvides(self.portal.site1, INavigationRoot)
        
        self.portal.invokeFactory('Document', 'd1')
        self.portal.site1.invokeFactory('Document', 'd2')

        catalog = getToolByName(self.portal, 'portal_catalog')

        lazy = catalog(portal_type='Document', path='/'.join(self.portal.getPhysicalPath()))
        results = [x.getId for x in lazy]
        self.failUnless('d1' in results)
        self.failUnless('d2' in results)

        # Simulate traversal
        notify(BeforeTraverseEvent(self.portal.site1, self.portal.REQUEST))
        
        lazy = catalog(portal_type='Document', path='/'.join(self.portal.getPhysicalPath()))
        results = [x.getId for x in lazy]
        self.failUnless('d1' in results)
        self.failUnless('d2' in results)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IntegrationTests))
    return suite