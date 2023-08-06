# -*- coding: utf-8 -*-
#
# File: Mlango.py
#
# Copyright (c) 2008 by Goldmund-Wyldebeast & Wunderliebe
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Goldmund-Wyldebeast & Wunderliebe <info@gw20e.com>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


PROJECTNAME = "Mlango"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'MlangoDashboard': 'Mlango: Add MlangoDashboard',
    'MlangoViewlet': 'Mlango: Add MlangoViewlet',
    'MlangoRSSViewlet': 'Mlango: Add MlangoRSSViewlet',
    'MlangoCustomViewlet': 'Mlango: Add MlangoCustomViewlet',
}

setDefaultRoles('Mlango: Add MlangoDashboard', ('Manager','Owner'))
setDefaultRoles('Mlango: Add MlangoViewlet', ('Manager','Owner'))
setDefaultRoles('Mlango: Add MlangoRSSViewlet', ('Manager','Owner'))
setDefaultRoles('Mlango: Add MlangoCustomViewlet', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here

VIEWLET_DEFAULTS = {'col_0':'','col_1':''}
TOOL_ID = 'portal_mlangotool'

VIEWLETS = (
            {'id': 'help',
             'title': 'Info',
             'icon': 'help.gif',
             'help': 'This viewlet contains Mlango relevant information.',
             'fixed': 1,
             },
             {'id': 'poweredby',
             'title': 'Power',
             'icon': 'user.gif',
             'help': 'Mlang is brought to you by Goldmund-Wyldebeast&Wunderliebe',
             'macro': 'here/powered_by_viewlet/macros/body',
             'fixed': -1,
             },
            )
DEBUG = True
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.Mlango.AppConfig import *
except ImportError:
    pass
