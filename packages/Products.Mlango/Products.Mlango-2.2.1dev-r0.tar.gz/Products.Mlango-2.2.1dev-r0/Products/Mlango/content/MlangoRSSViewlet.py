# -*- coding: utf-8 -*-
#
# File: MlangoRSSViewlet.py
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

    StringField(
        name='rssurl',
        widget=StringField._properties['widget'](
            label="RSS feed url",
            description="Enter the full URL to the rss feed you want this viewlet to display.",
            label_msgid='Mlango_label_rssurl',
            description_msgid='Mlango_help_rssurl',
            i18n_domain='Mlango',
        ),
        required=True,
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MlangoRSSViewlet_schema = BaseSchema.copy() + \
    getattr(MlangoViewlet, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class MlangoRSSViewlet(BaseContent, MlangoViewlet, BrowserDefaultMixin):
    """MlangoViewlet which has an RSS feed as content
    """
    security = ClassSecurityInfo()
    implements(interfaces.IMlangoRSSViewlet)

    meta_type = 'MlangoRSSViewlet'
    _at_rename_after_creation = True

    schema = MlangoRSSViewlet_schema

    ##code-section class-header #fill in your manual code here
    _contenttemplate = ViewPageTemplateFile('MlangoRSSViewlet.pt')
    ##/code-section class-header

    # Methods


registerType(MlangoRSSViewlet, PROJECTNAME)
# end of class MlangoRSSViewlet

##code-section module-footer #fill in your manual code here
##/code-section module-footer



