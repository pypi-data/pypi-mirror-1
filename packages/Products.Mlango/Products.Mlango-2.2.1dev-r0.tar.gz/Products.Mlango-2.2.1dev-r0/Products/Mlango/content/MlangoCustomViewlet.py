# -*- coding: utf-8 -*-
#
# File: MlangoCustomViewlet.py
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
from Products.Mlango.content.MlangoViewlet import MlangoViewlet
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Mlango.config import *

# additional imports from tagged value 'import'
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    TextField(
        name='content',
        widget=TextAreaWidget
    ,
        required=True,
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MlangoCustomViewlet_schema = BaseSchema.copy() + \
    getattr(MlangoViewlet, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class MlangoCustomViewlet(BaseContent, MlangoViewlet, BrowserDefaultMixin):
    """MlangoViewlet Class which can have custom content as content.
    """
    security = ClassSecurityInfo()
    implements(interfaces.IMlangoCustomViewlet)

    meta_type = 'MlangoCustomViewlet'
    _at_rename_after_creation = True

    schema = MlangoCustomViewlet_schema

    ##code-section class-header #fill in your manual code here
    _contenttemplate = ViewPageTemplateFile('MlangoCustomViewlet.pt')
    ##/code-section class-header

    # Methods


registerType(MlangoCustomViewlet, PROJECTNAME)
# end of class MlangoCustomViewlet

##code-section module-footer #fill in your manual code here
##/code-section module-footer



