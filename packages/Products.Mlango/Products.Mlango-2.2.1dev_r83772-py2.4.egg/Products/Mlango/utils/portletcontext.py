from types import StringTypes

from zope.interface import implements, Interface
from zope.component import adapts

from Acquisition import aq_parent, aq_inner, aq_base

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.portlets.portletcontext import ContentContext
from plone.portlets.constants import CONTEXT_CATEGORY


class MlangoDashboardContext(ContentContext):
    
    """ A portlet context for the Mlango dashboard content type. This filters out all
        global categories.
    """

    def globalPortletCategories(self, placeless=False):

        return [] #(CONTEXT_CATEGORY, self.context.getPhysicalPath())]
