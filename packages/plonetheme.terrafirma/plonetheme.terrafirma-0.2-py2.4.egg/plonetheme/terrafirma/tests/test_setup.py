import unittest
from plonetheme.terrafirma.tests.base import TerrafirmaTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(TerrafirmaTestCase):
    
    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
        self.css = getToolByName(self.portal, 'portal_css')
        self.skins = getToolByName(self.portal, 'portal_skins')
    
    def test_theme_installed(self):
        layer = self.skins.getSkinPath('Terrafirma Theme')
        self.failUnless('plonetheme_terrafirma_styles' in layer)
        self.assertEquals('Terrafirma Theme', self.skins.getDefaultSkin())
        cssTitles = [n.getTitle() for n in self.css.resources]
        self.failUnless('Terrafirma CSS' in cssTitles)
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
