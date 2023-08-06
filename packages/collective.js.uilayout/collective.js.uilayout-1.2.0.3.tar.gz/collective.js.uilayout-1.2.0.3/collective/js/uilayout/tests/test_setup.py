"""This is an integration "unit" test. It uses PloneTestCase, but does not
use doctest syntax.

You will find lots of examples of this type of test in CMFPlone/tests, for 
example.
"""

import unittest
from collective.js.uilayout.tests.base import UILayoutTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(UILayoutTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """
        self.jsregistry = getToolByName(self.portal, 'portal_javascripts')
        self.cssregistry = getToolByName(self.portal, 'portal_css')
        self.quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        
    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """
        
    def test_products_installed(self):
        # This is a simple test. The method needs to start with the name
        # 'test'. 

        # Look at the Python unittest documentation to learn more about hte
        # kinds of assertion methods which are available.

        # PloneTestCase has some methods and attributes to help with Plone.
        # Look at the PloneTestCase documentation, but briefly:
        # 
        #   - self.portal is the portal root
        #   - self.folder is the current user's folder
        #   - self.logout() "logs out" so that the user is Anonymous
        #   - self.setRoles(['Manager', 'Member']) adjusts the roles of the current user
        self.failUnless(self.quickinstaller.isProductInstalled('collective.js.jquery'))
        self.failUnless(self.quickinstaller.isProductInstalled('collective.js.jqueryui'))
        self.failUnless(self.quickinstaller.isProductInstalled('collective.js.uilayout'))
        
    def test_javascript_installed(self):
        self.failUnless(self.jsregistry.getResource('++resource++jquery.layout.min.js') is not None)
    
    def test_css_installed(self):
        self.failUnless(self.cssregistry.getResource('++resource++jquery.layout.css') is not None)
        self.failUnless(self.cssregistry.getResource('++resource++jquery.layout.plonekss.css') is not None)
            
    # Keep adding methods here, or break it into multiple classes or
    # multiple files as appropriate. Having tests in multiple files makes
    # it possible to run tests from just one package:
    #
    #   ./bin/instance test -s collective.js.uilayout -t test_setup

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
