# -*- coding: utf-8 -*-
#
# File: MlangoViewlet.py
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

# additional imports from tagged value 'import'
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

##code-section module-header #fill in your manual code here
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.compress import xhtml_compress
##/code-section module-header

schema = Schema((

    ImageField(
        name='viewleticon',
        widget=ImageField._properties['widget'](
            label="Viewlet Icon",
            description="Please upload the image that should be used in the toolbar of the viewlet as Icon.",
            label_msgid='Mlango_label_viewleticon',
            description_msgid='Mlango_help_viewleticon',
            i18n_domain='Mlango',
        ),
        storage=AttributeStorage(),
    ),
    TextField(
        name='help',
        widget=TextAreaWidget(
            label="Viewlet Help",
            description="Enter the help for this viewlet here, it will become visible when people press the help button for the viewlet.",
            label_msgid='Mlango_label_help',
            description_msgid='Mlango_help_help',
            i18n_domain='Mlango',
        ),
    ),
    IntegerField(
        name='fixed',
        default=-1,
        widget=IntegerField._properties['widget'](
            description="In which column should this viewlet be fixed? Default is -1 (not fixed). First column is 0, second column 1.",
            label='Fixed',
            label_msgid='Mlango_label_fixed',
            description_msgid='Mlango_help_fixed',
            i18n_domain='Mlango',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MlangoViewlet_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class MlangoViewlet(BaseContent, BrowserDefaultMixin):
    """ Super class for all MlangoViewlets, the fields in this class are common for all viewlets.
    Same for the _viewlettemplate, which is shared by all viewlets as well.
    If no _contenttemplate is defined in a viewlet, it uses the "error" template defined here.
    """
    security = ClassSecurityInfo()
    implements(interfaces.IMlangoViewlet)

    meta_type = 'MlangoViewlet'
    _at_rename_after_creation = True

    schema = MlangoViewlet_schema

    ##code-section class-header #fill in your manual code here

    #_viewlettemplate is used by all MlangoViewlets as there frame.
    _viewlettemplate = ViewPageTemplateFile('MlangoViewlet.pt')

    #_contenttemplate is unique for each viewlet contains way to render their content
    _contenttemplate = ViewPageTemplateFile('MlangoViewlet_error.pt')

    ##/code-section class-header

    # Methods

    security.declarePublic('returnTemplate')
    def returnTemplate(self):
        return self._viewlettemplate

    security.declarePublic('returnContentTemplate')
    def returnContentTemplate(self):
        return self._contenttemplate


registerType(MlangoViewlet, PROJECTNAME)
# end of class MlangoViewlet

##code-section module-footer #fill in your manual code here
##/code-section module-footer



