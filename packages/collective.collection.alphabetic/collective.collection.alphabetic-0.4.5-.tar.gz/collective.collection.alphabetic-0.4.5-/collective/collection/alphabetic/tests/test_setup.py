# -*- coding: utf-8 -*-
import unittest
from Products.CMFCore.utils import getToolByName
from base import CollectionAlphabeticTestCase
class TestSetup(CollectionAlphabeticTestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')
        self.propertiestool = getToolByName(self.portal, 'portal_properties')

## propertiestool.xml

    def test_character_tokens(self):
        self.assertEquals("boolean", self.propertiestool.collection_alphabetic_properties.getPropertyType('use_alphabet'))
        self.assertEquals("tokens", self.propertiestool.collection_alphabetic_properties.getPropertyType('character_tokens'))


## actions.xml

#    def test_contact_action_installed(self):
#        self.failUnless('contact' in self.portal.portal_actions.site_actions.objectIds())

#    def test_mystuff_action_installed(self):
#        self.failUnless('mystuff' in self.portal.portal_actions.user.objectIds())

#    def test_preferences_action_installed(self):
#        self.failUnless('preferences' in self.portal.portal_actions.user.objectIds())

#    def test_login_action_installed(self):
#        self.failUnless('login' in self.portal.portal_actions.user.objectIds())

#    def test_join_action_installed(self):
#        self.failUnless('join' in self.portal.portal_actions.user.objectIds())

##    def test_cart_action_installed(self):
##        self.failUnless('cart' in self.portal.portal_actions.user.objectIds())

##    def test_information_action_installed(self):
##        self.failUnless('information' in self.portal.portal_actions.user.objectIds())

#    def test_sharing_permissions(self):
#        self.assertEquals(('Content rules: Manage rules',), self.portal.portal_actions.object.local_roles.getProperty('permissions'))

### rolemap.xml
#    def test_manage_own_portlet_permission(self):
#        permissions = [r['name'] for r in self.portal.rolesOfPermission('Portlets: Manage own portlets') if r['selected']]
#        self.failIf('Member' in permissions)
#        self.failUnless('Manager' in permissions)

#    def test_add_portal_member_permission(self):
#        permissions = [r['name'] for r in self.portal.rolesOfPermission('Add portal member') if r['selected']]
#        self.failUnless('Anonymous' in permissions)
#        self.failUnless('Manager' in permissions)

### mall.theme skin installation

#    def test_theme_installed(self):
#        skins = getToolByName(self.portal, 'portal_skins')
#        layer = skins.getSkinPath('MallTheme')
#        self.failUnless('mall_theme_custom_templates' in layer)
#        self.assertEquals('MallTheme', skins.getDefaultSkin())

#    def test_mallcontent_skin_installed(self):
#        skins = getToolByName(self.portal, 'portal_skins')
#        layer = skins.getSkinPath('Plone Default')
#        self.failUnless('mall_scripts_and_templates' in layer)

### language

#    def test_available_languages(self):
#        ltool = getToolByName(self.portal, 'portal_languages')
#        self.assertEquals('ja', ltool.getDefaultLanguage())
#        self.assertEqual([('en', u'English'), ('fi', u'Finnish'), ('ja', u'Japanese')], ltool.listSupportedLanguages())

#    def test_language_flag(self):
#        ltool = getToolByName(self.portal, 'portal_languages')
#        self.assertEquals(False, ltool.showFlags())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
