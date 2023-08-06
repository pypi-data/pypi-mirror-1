import os
import selenium
import transaction

import Lifetime
from Testing.ZopeTestCase import utils

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, default_user, default_password
from Products.PloneTestCase.layer import PloneSite as PloneLayer

class SeleniumLayer:
 
    # The Selenium RC client - per layer
    _selenium = None

    # Connection parameters
    _server = os.environ.get('SELENIUM_HOST', 'localhost')
    _port = os.environ.get('SELENIUM_PORT', '4444')
    _browser = os.environ.get('SELENIUM_BROWSER', '*chrome')

    # ID of the site to load
    _site = 'plone'
    
    @classmethod
    def setUp(cls):
        """Start the Selenium server and the ZServer thread
        """
        
        # Start the Zope server with five threads
        host, port = utils.startZServer(5)
        url = "http://%s:%s/%s" % (host, port, cls._site)
        
        cls._selenium = selenium.selenium(cls._server, cls._port, cls._browser, url)
        cls._selenium.start()

    @classmethod
    def tearDown(cls):
        """Stop the Selenium server and the ZServer thread
        """
        
        cls._selenium.stop()
        Lifetime.shutdown(0, fast=1)

class SeleniumPloneLayer(PloneLayer, SeleniumLayer):
    pass

class SeleniumTestCase(FunctionalTestCase):
    """Base class for tests that need Selenium support
    """
    
    layer = SeleniumPloneLayer
    
    @property
    def selenium(self):
        return self.layer._selenium
        
    def open(self, path="/", site_name="plone"):
        # ensure we have a clean starting point
        transaction.commit()
        self.selenium.open("/%s/%s" % (site_name, path,))
        
    def wait(self, timeout="30000"):
        self.selenium.wait_for_page_to_load(timeout)
        
    def login_user(self, username=default_user, password=default_password):
        self.open("/login")
        self.selenium.type("name=__ac_name", username)
        self.selenium.type("name=__ac_password", password)
        self.selenium.click("submit")
        self.wait()
