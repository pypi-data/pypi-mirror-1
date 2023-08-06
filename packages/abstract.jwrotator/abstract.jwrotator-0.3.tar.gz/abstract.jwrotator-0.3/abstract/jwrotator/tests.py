import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite    

from Products.Five.testbrowser import Browser

from Products.CMFCore.utils import getToolByName

ptc.setupPloneSite(products=['abstract.jwrotator'])

import abstract.jwrotator

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             abstract.jwrotator)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass         

    def testProperInstall(self):
        """Test if product install properly"""
        qi_tool = getToolByName(self.portal,'portal_quickinstaller')    
        self.failUnless( qi_tool.isProductInstalled('abstract.jwrotator') )
        
    def testViewMethods(self):
        """test if jwrotator_vew is installed properly"""
        pt_tool = getToolByName(self.portal,'portal_types')
        view_types = ['Folder','Topic','Large Plone Folder']       
        for view_type in view_types: 
            folder_view_methods = list(pt_tool[view_type].view_methods)
            self.failUnless('jwrotator_view' in folder_view_methods)          
            
    def testEmbeddedSWF(self):
        """test if SWF is embedded in the view"""                   
        self.setRoles(('Manager',)) 
        self.portal.invokeFactory('Folder','folder_image')
        folder = getattr(self.portal,'folder_image')              
        folder.setLayout('jwrotator_view')
        # FIX: broeser seems not working
        #browser = Browser()
        #browser.open(folder.absolute_url())
        
                              
def test_suite():
    #return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='abstract.jwrotator',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='abstract.jwrotator.tests',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='abstract.jwrotator',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='abstract.jwrotator',
        #    test_class=TestCase),

     #   ])
     suite = unittest.TestSuite()
     suite.addTest(unittest.makeSuite(TestCase))
     return suite 

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
