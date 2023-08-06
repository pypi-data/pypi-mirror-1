import unittest
from Products.CMFCore.utils import getToolByName
from Products.ColorField.tests.base import ColorFieldTestCase

from Products.CMFPlone.tests import dummy

class TestSetup(ColorFieldTestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        self.acl_users= getToolByName(self.portal, 'acl_users')
        self.membership = getToolByName(self.portal, 'portal_membership')

    def test_skin_installed(self):
        skins = getToolByName(self.portal, 'portal_skins')
        layer = skins.getSkinPath('Plone Default')
        self.failUnless('ColorField' in layer)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
