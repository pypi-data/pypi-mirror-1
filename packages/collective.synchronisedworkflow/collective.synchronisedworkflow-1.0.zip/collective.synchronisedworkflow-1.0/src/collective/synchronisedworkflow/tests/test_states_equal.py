from unittest import TestSuite, makeSuite

from Products.PloneTestCase import ptc
    
from base import installed

class TestStates(ptc.PloneTestCase):
    
    layer = installed
    
    def afterSetUp(self):
        self.portal.portal_languages.addSupportedLanguage('de')
    
    def test_newly_created_content_should_have_the_same_wf_state(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        self.assertEqual(wft.getCatalogVariablesFor(en), wft.getCatalogVariablesFor(de))

    def test_transition_of_canonical_item_after_translation_propagates(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        
        wft.doActionFor(en, "submit")
        
        assert not de.isOutdated() # We don't want wf changes to mark outdated
        
        self.assertEqual(wft.getCatalogVariablesFor(en), wft.getCatalogVariablesFor(de))
    
    def test_transition_of_noncanonical_item_propagates(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        
        wft.doActionFor(de, "submit")
        
        self.assertEqual(wft.getCatalogVariablesFor(en), wft.getCatalogVariablesFor(de))

    def test_transition_of_canonical_item_retained_on_new_content(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        wft.doActionFor(en, "submit")
        
        de = en.addTranslation("de")
        self.assertEqual(wft.getCatalogVariablesFor(en), wft.getCatalogVariablesFor(de))

class TestComplexPermissions(ptc.PloneTestCase):
    
    layer = installed
    
    def test_assumption_cant_publish_without_special_roles(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        
        wft.doActionFor(de, "submit")        

        self.assertRaises(Exception, wft.doActionFor, en, "publish")
    
    def test_transition_fails_if_no_permissions_on_translation(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        
        wft.doActionFor(de, "submit")        
                
        # Give permissions on en
        en.manage_addLocalRoles('test_user_1_', ['Reviewer', ])
        self.portal.REQUEST.__annotations__.clear() # borg.localroles caching
        self.assertRaises(Exception, wft.doActionFor, en, "publish")

    def test_publishing_works_if_special_roles_are_avaiable_on_all_translations(self):
        wft = self.portal.portal_workflow
        self.folder.invokeFactory("Document", "test", title="Test", Language="en")
        en = self.folder['test']
        de = en.addTranslation("de")
        
        wft.doActionFor(de, "submit")        
                
        # Give permissions on en
        en.manage_addLocalRoles('test_user_1_', ['Reviewer', ])
        de.manage_addLocalRoles('test_user_1_', ['Reviewer', ])
        self.portal.REQUEST.__annotations__.clear() # borg.localroles caching

        wft.doActionFor(en, "publish")
        self.assertEqual(wft.getCatalogVariablesFor(en), wft.getCatalogVariablesFor(de))
        self.assertEqual(wft.getCatalogVariablesFor(en)['review_state'], 'published')

class TestVeryRestrictiveStates(ptc.FunctionalTestCase):
    
    layer = installed
    
    def test_one(self):
        from zope.testbrowser.browser import Browser
        browser = Browser()



def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestStates))
    suite.addTest(makeSuite(TestComplexPermissions))
    #suite.addTest(makeSuite(TestVeryRestrictiveStates))
    return suite
