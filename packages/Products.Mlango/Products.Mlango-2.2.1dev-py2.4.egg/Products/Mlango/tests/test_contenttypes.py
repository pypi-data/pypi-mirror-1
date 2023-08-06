import os
import unittest
import StringIO
from Globals import InitializeClass, package_home
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import _createObjectByType

from Products.Mlango.tests.base import MlangoTestCase
import Products.Mlango.content.MlangoViewlet


def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(package_home(globals()), 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data
    
TEST_GIF = loadImage('test.gif')



class TestContentTypes(MlangoTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])

        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.portalRoot =  self.portal.portal_url.getPortalObject()
        
        self.mlangoDashboard = "MlangoDashboard"
        self.mlangoViewlet = "MlangoViewlet"
        self.mlangoRSSViewlet = "MlangoRSSViewlet"
        self.mlangoCustomViewlet = "MlangoCustomViewlet"
        
        self.types = [self.mlangoViewlet, self.mlangoRSSViewlet, self.mlangoCustomViewlet]
        
    def testCreateTypes(self):
        """ Create content types and test workflow
            presence.
        """
        for type in self.types:
            typeId = self.portal.generateUniqueId()
            typeTitle = "%s title" % type
            
            _createObjectByType(type, self.portal, typeId)
            
            obj = getattr(self.portal, typeId)
            obj.setTitle(typeTitle)
            
            self.assertEqual(obj.getId(), typeId)
            self.assertEqual(obj.Title(), typeTitle)
    
    def testMlangoDashboard(self):
        """
        """
        dashboardId = 'dashboard'
        dashboardTitle = 'Mlango dashboard'
        
        _createObjectByType(self.mlangoDashboard, self.portal, dashboardId)
        
        dashboard = getattr(self.portal, dashboardId)
        
        # test fields in schema
        dashboard.setCols(4)
        self.assertEqual(dashboard.getCols(), 4)
        
        flow = self.workflow.getWorkflowsFor(dashboard)[0]
        self.failUnless(flow.id == 'dashboard_workflow')
    
    
    def testMlangoViewlet(self):
        """ Test viewlet
        """
        viewletId = "myViewlet"
        viewletHelp = "This is a help string"
             
        _createObjectByType(self.mlangoViewlet, self.portal, viewletId)
        
        contentIndex = os.path.join(\
            os.path.dirname(Products.Mlango.content.MlangoViewlet.__file__))
        
        viewlet = getattr(self.portal, viewletId)
        
        # test fields in schema
        viewlet.setViewleticon(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnless(viewlet.getViewleticon())
        
        viewlet.setHelp(viewletHelp)
        self.assertEqual(viewlet.getHelp(), viewletHelp)
        
        viewlet.setFixed(-1)
        self.assertEqual(viewlet.getFixed(), -1)
      
        self.failUnless(viewlet.returnTemplate())
        self.failUnless(viewlet.returnContentTemplate()) 


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentTypes))
    return suite
