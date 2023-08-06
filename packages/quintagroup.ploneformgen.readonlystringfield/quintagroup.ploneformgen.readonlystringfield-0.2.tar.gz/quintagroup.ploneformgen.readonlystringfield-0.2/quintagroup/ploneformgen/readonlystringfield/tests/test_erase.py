import unittest
import transaction
from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager
from Testing import ZopeTestCase as ztc
from Products.CMFCore.utils import getToolByName
from  Products.PloneTestCase.layer import PloneSiteLayer

from quintagroup.ploneformgen.readonlystringfield.tests.base import \
    ReadOnlyStringFieldTestCase


class TestErase(ReadOnlyStringFieldTestCase):
    # we use here nested layer for not to make an impact on
    # the rest test cases, this test case check uninstall procedure
    # thus it has to uninstall package which will be required to
    # be installed for other test cases
    class layer(PloneSiteLayer):
        @classmethod
        def setUp(cls):
            app = ztc.app()
            portal = app.plone
            
            # elevate permissions
            user = portal.getWrappedOwner()
            newSecurityManager(None, user)

            tool = getToolByName(portal, 'portal_quickinstaller')
            product_name = 'quintagroup.ploneformgen.readonlystringfield'
            if tool.isProductInstalled(product_name):
                tool.uninstallProducts([product_name,])
            
            # drop elevated perms
            noSecurityManager()
            
            transaction.commit()
            ztc.close(app)
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
    
    def test_factoryTool(self):
        tool = getToolByName(self.portal, 'portal_factory')
        self.failIf('FormReadonlyStringField' in tool._factory_types.keys(),
            'FormReadonlyStringField type is still in portal_factory tool.')
    
    def test_typesTool(self):
        tool = getToolByName(self.portal, 'portal_types')
        self.failIf('FormReadonlyStringField' in tool.objectIds(),
            'FormReadonlyStringField type is still in portal_types tool.')
    
    def test_propertiesTool(self):
        tool = getToolByName(self.portal, 'portal_properties')
        navtree = tool.navtree_properties
        self.failIf('FormReadonlyStringField' in navtree.metaTypesNotToList,
            'FormReadonlyStringField is still in metaTypesNotToList property.')
        site = tool.site_properties
        self.failIf('FormReadonlyStringField' in site.types_not_searched,
            'FormReadonlyStringField is still in types_not_searched property.')
    
    def test_skinsTool(self):
        tool = getToolByName(self.portal, 'portal_skins')
        self.failIf('readonlystringfield' in tool.objectIds(),
            'There is still readonlystringfield folder in portal_skins.')
        for path_id, path in tool._getSelections().items():
            layers = [l.strip() for l in path.split(',')]
            self.failIf('readonlystringfield' in layers,
                'readonlystringfield layer is still in %s.' % path_id)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestErase))
    return suite
