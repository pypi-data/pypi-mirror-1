# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by Goldmund-Wyldebeast & Wunderliebe
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Goldmund-Wyldebeast & Wunderliebe <info@gw20e.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('Mlango: setuphandlers')
from Products.Mlango.config import PROJECTNAME
from Products.Mlango.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotMlangoProfile(context):
    return context.readDataFile("Mlango_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMlangoProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMlangoProfile(context): return
    site = context.getSite()



##code-section FOOT

#WIETZE: disable the updateRoleMappings and fixTools...

def dummyUpdateRoleMappings(context):
    """do nothing..."""
    pass

updateRoleMappings = dummyUpdateRoleMappings

def dummyFixTools(context):
    """do nothing..."""
    pass

fixTools = dummyFixTools

##/code-section FOOT
