# -*- coding: utf-8 -*-
#
# File: MlangoDashboard.py
#
# Copyright (c) 2008 by Goldmund-Wyldebeast & Wunderliebe
# Generator: ArchGenXML Version 2.0-beta11
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

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    IntegerField(
        name='cols',
        default=4,
        widget=IntegerField._properties['widget'](
            label="Number of columns",
            description="How many columns does the dashboard have?",
            label_msgid="cols_label",
            description_msgid="cols_help",
            i18n_domain="mlango",
        ),
        required=True,
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MlangoDashboard_schema = BaseSchema.copy() + \
    schema.copy()

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

    ##code-section class-header #fill in your manual code here
    aliases = {
        '(Default)'  : 'mlango_dashboard_view', # for now, use the dashboard_view by default
        'view'       : 'mlango_dashboard_view',
        'index.html' : 'mlango_dashboard_view',
        'edit'       : 'atct_edit',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form',
        'gethtml'    : '',
        'mkdir'      : '',
        }

    ##/code-section class-header

    # Methods


registerType(MlangoDashboard, PROJECTNAME)
# end of class MlangoDashboard

##code-section module-footer #fill in your manual code here
##/code-section module-footer



