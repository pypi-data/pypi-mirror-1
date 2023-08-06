from Products.PloneTestCase import PloneTestCase as ptc
from collective.ploneseltest import SeleniumTestCase

ptc.setupPloneSite()

class ExampleTestCase(SeleniumTestCase):

    def afterSetUp(self):
        """Setup for each test
        """
        self.setRoles(['Manager'])
        self.login_user()
        
    def test_create_foo1(self):
        self.failIf(self.selenium.is_text_present("Foo"))
        self.selenium.click("//dl[@id='plone-contentmenu-factories']/dt/a/span[1]")
        self.selenium.click("document")
        self.wait()
        self.selenium.type("title", "Foo")
        self.selenium.click("name=form_submit")
        self.wait()
        self.failUnless(self.selenium.is_text_present("Foo"))
        
        
    def test_create_foo2(self):
        # we do this again to ensure they run in isolation
        self.failIf(self.selenium.is_text_present("Foo"))
        self.selenium.click("//dl[@id='plone-contentmenu-factories']/dt/a/span[1]")
        self.selenium.click("document")
        self.wait()
        self.selenium.type("title", "Foo")
        self.selenium.click("name=form_submit")
        self.wait()
        self.failUnless(self.selenium.is_text_present("Foo"))
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ExampleTestCase))
    return suite