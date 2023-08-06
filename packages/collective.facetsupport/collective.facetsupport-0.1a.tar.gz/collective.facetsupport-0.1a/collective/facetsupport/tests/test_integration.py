"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""
import unittest
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from collective.facetsupport.tests import base

#Imports for tests
from zope.publisher.browser import TestRequest
from collective.facetsupport.interfaces import IFacetBuilder
from collective.facetsupport.utilities import FacetBuilder
from collective.facetsupport.config import DEFAULT_INDEXES

ptc.setupPloneSite()

class TestIntegration(base.TestCase):
    """Test integration
    """
    #layer = contentstructure
    
    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """
        super(TestIntegration, self).afterSetUp()
            
        self.catalog = self.portal.portal_catalog

    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """
        
    def testFacetBuilderIntegration(self):
        request = TestRequest()
        adapter = IFacetBuilder(self.portal, request)
        
        self.failUnless(adapter,'FacetBuilder not found')
        self.failUnless(IFacetBuilder.providedBy(adapter), 'IFacetBuilder not provided by FacetBuilder')
        self.failUnless(IFacetBuilder.implementedBy(FacetBuilder), "FacetBuilder doesn't implement IFacetBuilder")

    
    def testDummyStructure(self):
        doc = self.portal.dummy_container.get('doc1',None)
        self.failUnless(doc)
        self.assertEquals(doc.Subject(),('Apple','Banana','Orange','Lemon'))
        collection = self.portal.get('collection',None)
        self.failUnless(collection)
        #first-page is also a page, so 11 is right! :)
        self.assertEquals(len(collection.queryCatalog()),11)
        
    def testDummyInCatalog(self):
        self.failUnless(self.catalog(Subject='Apple'))
        self.assertEquals(len(self.catalog()),20)
    
    def testInlineFacetResultView(self):
        view = self.portal.restrictedTraverse('@@inline_facet_result',None)
        self.failUnless(view)

    def testInlineFacetMenuView(self):
        view = self.portal.restrictedTraverse('@@inline_facet_menu',None)
        self.failUnless(view)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """ 
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntegration))
    return suite
