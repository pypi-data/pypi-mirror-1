# -*- coding: utf-8 -*-
#
# File: MlangoTool.py
#
# Copyright (c) 2008 by Goldmund-Wyldebeast & Wunderliebe
# Generator: ArchGenXML Version 2.0-beta11
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Goldmund-Wyldebeast & Wunderliebe <info@gw20e.com>"""
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
import os
from UserSettingsStorage import UserSettingsStorage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import *
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Mlango.config import *
from Globals import PersistentMapping
import interfaces
from Products.CMFCore.utils import getToolByName
##/code-section module-header

from zope.interface import implements
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from persistent import Persistent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


class MlangoTool(SimpleItem,UniqueObject,Persistent):
    """
    """

    ##code-section class-header_MlangoTool #fill in your manual code here


    _www = os.path.join(os.path.dirname(__file__), '../www')

    meta_type = 'MlangoTool'
    _at_rename_after_creation = True

    isPrincipiaFolderish = True # Show up in the ZMI
    security = ClassSecurityInfo()

    manage_options = (
                      {'label': 'Info', 'action': 'info'},
                      {'label': 'Viewlets', 'action' : 'manage_viewlets'},
                      {'label': 'Users', 'action' : 'manage_users'},
                      )

    security.declareProtected(ManagePortal, 'manage_viewlets')
    manage_viewlets = PageTemplateFile('manage_viewlets', _www)

    security.declareProtected(ManagePortal, 'manage_users')
    manage_users = PageTemplateFile('manage_users', _www)

    security.declareProtected(View, 'info')
    info = PageTemplateFile('info', _www)

    ##/code-section class-header_MlangoTool


    def __init__(self, id=None):
        self._viewletregistry = {}
        self._usersettingsstorage = UserSettingsStorage()

    def registerViewlet(self, viewlet):
        self._viewletregistry[viewlet.UID()] = {'fixed': viewlet.getFixed()}
        self._changes()

    def unregisterViewlet(self, viewlet):
        if viewlet.UID() in self._viewletregistry.keys():
            del self._viewletregistry[viewlet.UID()]
            self._changes()

    def listViewletIds(self):
        return self._viewletregistry.keys()

    def getViewlet(self, id):
        tool = getToolByName(self, "uid_catalog")
        list = tool(UID=id)
        if len(list) > 0:
            return list[0].getObject()
        else:
            return None

    def listUsers(self):
        return self._usersettingsstorage.keys()
    
    def listBoardSettings(self, uid):
        return self._usersettingsstorage.listBoardsForUser(uid)

    def getUserSettings(self, user_id, dashboard_id, prefix=None):
        return self._usersettingsstorage.getUserSettings(user_id, dashboard_id, prefix=prefix)

    def setUserSettings(self, user_id, dashboard_id, data):
        return self._usersettingsstorage.setUserSettings(user_id, dashboard_id, data)

    def updateUserSettings(self, user_id, dashboard_id, data):
        return self._usersettingsstorage.updateUserSettings(user_id, dashboard_id, data)

    def listViewletIdsByFixedProperty(self, colnumber):
        """ Find viewlets by a given property """
        return [key for key,value in self._viewletregistry.iteritems() if value['fixed'] == colnumber]
   
    def listAllBoardsWithSettings(self):
        return self._usersettingsstorage.listAllBoardsWithSettings()

    def at_post_edit_script(self):
        self.unindexObject()

    def _changes(self):
        self._p_changed = 1 # for persistence..


##code-section module-footer #fill in your manual code here

def registerAddedViewlet(viewlet, event):
    """Event handler for edited (and new) viewlets, when a contet type is made,
    this even is called several times. So we wait for it to leave the portal_factory 
    before registering, to prevent ghost viewlets to be present.
    """
    if viewlet.absolute_url().find("portal_factory") == -1:
        tool = getToolByName(viewlet, "portal_mlangotool")
        tool.registerViewlet(viewlet)

def unregisterDeletedViewlet(viewlet, event):
    """Event handler for deleting viewlets, unregisters a viewlet.
    """
    tool = getToolByName(viewlet, "portal_mlangotool")
    tool.unregisterViewlet(viewlet)


InitializeClass(MlangoTool)

##/code-section module-footer


