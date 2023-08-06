# -*- coding: utf-8 -*-
#
# File: UserSettingsStorage.py
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
from Products.CMFCore.permissions import *

##/code-section module-header

from Products.Mlango.config import VIEWLET_DEFAULTS
from zope.interface import implements
from Globals import PersistentMapping
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


class UserSettingsStorage(PersistentMapping):
    """
    """

    ##code-section class-header_UserSettingsStorage #fill in your manual code here
    ##/code-section class-header_UserSettingsStorage

    def getUserSettings(self, user_id,dashboard_id, prefix=None):

        
        if not prefix:
            return self.get(user_id, {}).get(dashboard_id, VIEWLET_DEFAULTS)
        else:
            data = {}
            for k in self.get(user_id, {}).get(dashboard_id, {}).keys():
                if k.startswith(prefix):
                    data[k] = self[user_id][dashboard_id][k]
            return data
            
    def listBoardsForUser(self, user_id):
            return self.get(user_id, None)
    
    def listAllBoardsWithSettings(self):
        """This method goes by all boards which users have settings for,
        and adds them to one big list which it returns.
        """
        allBoards = []
        for value in self.itervalues():
            allBoards = [key for key in value.keys() if key not in allBoards] + allBoards
        return allBoards
        
    def setUserSettings(self, user_id, dashboard_id, data):

        self[user_id][dashboard_id] = data;
        self._p_changed = 1 # why is this needed in PersistentMapping?

    def updateUserSettings(self, user_id, dashboard_id, data):

        if not self.has_key(user_id):
            self[user_id] = {};

        if not self[user_id].has_key(dashboard_id):
            self[user_id][dashboard_id] = {}

        for k in data.keys():
            self[user_id][dashboard_id][k] = data[k]

        self._p_changed = 1 # why is this needed in PersistentMapping?


##code-section module-footer #fill in your manual code here
##/code-section module-footer


