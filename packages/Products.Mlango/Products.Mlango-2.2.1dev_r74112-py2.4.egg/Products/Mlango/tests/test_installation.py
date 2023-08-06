"""This is an integration "unit" test. It uses PloneTestCase, but does not
use doctest syntax.

You will find lots of examples of this type of test in CMFPlone/tests, for 
example.
"""

import unittest

from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME

from Products.Mlango.tests.base import MlangoTestCase
from Products.CMFCore.utils import getToolByName

from Products.Mlango.config import TOOL_ID
from Products.Mlango.tools.MlangoTool import MlangoTool



class TestInstallation(MlangoTestCase):
    """ Tests installation of Mlango
    """
    
    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOL_ID)
        self.ttool = getattr(self.portal.aq_explicit, 'portal_types')
        self.cat = getattr(self.portal.aq_explicit, 'portal_catalog')
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.csstool = getToolByName(self.portal, CSSTOOLNAME)
        self.jstool = getToolByName(self.portal, JSTOOLNAME)
        
        self.configlets = ['MlangoTool',]


    def testToolInstalled(self):
        """ Mlango tool
        """
        t = getToolByName(self.portal, TOOL_ID, None)
        self.failUnless(t, t)
        self.failUnless(isinstance(t, MlangoTool), t.__class__)
        self.failUnlessEqual(t.meta_type, 'MlangoTool')
        self.failUnlessEqual(t.getId(), TOOL_ID)
        
        

    def testSkinInstalled(self):
        """ Portal skins
        """
        stool = getattr(self.portal.aq_explicit, 'portal_skins')
        ids = stool.objectIds()
        self.failUnless('mlango_images' in ids, ids)
        self.failUnless('mlango_styles' in ids, ids)        
        self.failUnless('mlango_templates' in ids, ids)        

    def testInstalledAllTypes(self):
        """ Portal types
        """
        # test that all types are installed well
        ttool = self.ttool
        ids = ('MlangoDashboard', 'MlangoViewlet', 'MlangoRSSViewlet',
               'MlangoCustomViewlet')

        tids = ttool.objectIds()
        for id in ids:
            self.failUnless(id in tids, (id, tids))
            tinfo = ttool[id]
            self.failUnless(tinfo.product == 'Mlango', tinfo.product)

    def testControlPanel(self):
        """ Plone control panel
        """
        for title in self.configlets:
            self.failUnless(title in [a.getAction(self)['id']
                                   for a in self.controlpanel.listActions()],
                            "Missing configlet with id '%s'" % title)
        
    def testCssToolExists(self):
        """ CSS tool
        """
        self.failUnless(CSSTOOLNAME in self.portal.objectIds())
       
    def testCssRegistry(self):
        """ CSS registry
        """
        installedStylesheetIds = self.csstool.getResourceIds()
        expected = ['mlango.css', 'borders.css']
        for e in expected:
            self.failUnless(e in installedStylesheetIds, e)

    def testJsToolExists(self):
        """ JS tool
        """
        self.failUnless(JSTOOLNAME in self.portal.objectIds())
    
    def testJsRegistry(self):
        """ JS registry
        """
        installedScriptIds = self.jstool.getResourceIds()
        expected = ['jquery.js',]
        for e in expected:
            self.failUnless(e in installedScriptIds, e)
        
    def testJsInstertedInPage(self):
        page = self.portal.index_html()
        self.failUnless("" in page)
        

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    return suite
