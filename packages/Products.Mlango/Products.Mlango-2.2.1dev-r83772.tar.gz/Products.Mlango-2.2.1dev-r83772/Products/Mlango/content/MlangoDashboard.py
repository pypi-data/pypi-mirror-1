# -*- coding: utf-8 -*-
#
# File: MlangoDashboard.py
#
# Copyright (c) 2008 by Goldmund-Wyldebeast & Wunderliebe
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Goldmund-Wyldebeast & Wunderliebe <info@gw20e.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Mlango.config import *

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MlangoDashboard_schema = BaseSchema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class MlangoDashboard(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IMlangoDashboard)

    meta_type = 'MlangoDashboard'
    _at_rename_after_creation = True

    schema = MlangoDashboard_schema

    ##/code-section class-header

    # Methods


registerType(MlangoDashboard, PROJECTNAME)
# end of class MlangoDashboard

##code-section module-footer #fill in your manual code here
##/code-section module-footer



