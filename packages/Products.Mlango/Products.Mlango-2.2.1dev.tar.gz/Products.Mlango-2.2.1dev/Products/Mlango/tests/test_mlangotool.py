"""This is an integration "unit" test. It uses PloneTestCase, but does not
use doctest syntax.

You will find lots of examples of this type of test in CMFPlone/tests, for 
example.
"""

import unittest

from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME

from Products.Mlango.tests.base import MlangoTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.Mlango.config import TOOL_ID
from Products.Mlango.tools.MlangoTool import MlangoTool



class TestMlangoTool(MlangoTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOL_ID)
        self.viewletId = 'custom-viewlet'
        
        _createObjectByType("MlangoCustomViewlet", self.portal, self.viewletId)
        self.viewlet = getattr(self.portal, self.viewletId)
        self.viewletUID = self.viewlet.UID()
        
        self.viewletData = {'col_0': '%s--' % self.viewletUID, 
                            'col_1': '', 'col_2': '', 'col_3': ''}
                
    def testRegisterViewlet(self):
        """ Register viewlet
        """
        self.tool.registerViewlet(self.viewlet)
 
        self.failUnless(self.viewletUID in self.tool.listViewletIds())

    def testGetViewlet(self):
        """ Get viewlet
        """
        self.failUnless(self.tool.getViewlet(self.viewletUID))
        
    def testUnregisterViewlet(self):
        """ Unregister viewlet
        """
        self.tool.unregisterViewlet(self.viewlet)
        
        self.failIf(self.viewletUID in self.tool.listViewletIds())
                
    def testUserSettings(self):
        """ Store and retrieve user settings
        """
        self.tool.updateUserSettings('dummy-member', 'dashboard' , self.viewletData)

        settingsGlobal = self.tool.getUserSettings('dummy-member', 'dashboard')
        settingsColZero = self.tool.getUserSettings('dummy-member', 'dashboard', 'col_0')
        
        self.assertEqual(settingsGlobal, self.viewletData)
        
        viewletDataCol = self.viewletData.copy()
        del viewletDataCol['col_1']
        del viewletDataCol['col_2']
        del viewletDataCol['col_3']
        self.assertEqual(settingsColZero, viewletDataCol)
        
        self.tool.setUserSettings('dummy-member', 'dashboard' , viewletDataCol)
        settingsGlobalAltered = self.tool.getUserSettings('dummy-member', 'dashboard')
        self.assertEqual(settingsGlobalAltered, viewletDataCol)
        
    def testListUsers(self):
        """ List stored users
        """
        self.tool.updateUserSettings('dummy-member1', 'dashboard' , self.viewletData)
        self.tool.updateUserSettings('dummy-member2', 'dashboard' , self.viewletData)
        
        listUsers = self.tool.listUsers()
        self.assertEqual(len(listUsers), 2)
        self.failUnless('dummy-member1' in listUsers)
        self.failUnless('dummy-member2' in listUsers)        
    
    def testListBoardSettings(self):
        """ List of dashboard(s)
        """
        self.tool.updateUserSettings('dummy-member', 'dashboard' , self.viewletData)
        self.assertEqual(self.tool.listAllBoardsWithSettings(), ['dashboard',])
        
        

    def testFixedViewlet(self):
        """ Get fixed viewlets
        """
        viewletId = 'fixed-viewlet'
        _createObjectByType("MlangoCustomViewlet", self.portal, viewletId)
        viewlet = getattr(self.portal, viewletId)
        viewlet.setFixed(0)
        viewlet.reindexObject()
        self.tool.registerViewlet(viewlet)
        
        self.tool.listViewletIdsByFixedProperty(0)
    
    
def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMlangoTool))
    return suite
