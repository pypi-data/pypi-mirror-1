from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_base
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.portlets.constants import GROUP_CATEGORY, CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.storage import UserPortletAssignmentMapping
from plone.app.portlets.browser.manage import ManageDashboardPortlets
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.browser.manage import ManageGroupPortlets

from plone.app.portlets import utils
from plone.memoize.view import memoize


class ManageGroupDashboard(ManageDashboardPortlets):
    
    @property
    def category(self):
        return GROUP_CATEGORY
        
    @property
    def key(self):
        return self.request['key']
    
    def __init__(self, context, request):
        super(ManageGroupDashboard, self).__init__(context, request)
        self.request.set('disable_border', True)

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        key = self.request['key']
        return '%s/++groupportlets++%s+%s' % (baseUrl, manager.__name__, key)

    def getAssignmentsForManager(self, manager):
        key = self.request['key']
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(key, None)
        if mapping is None:
            mapping = category[key] = PortletAssignmentMapping(manager=manager.__name__,
                                                               category=GROUP_CATEGORY,
                                                               name=key)
        return mapping.values()
    
    
    def group(self):
        return self.request['key']


class ManageContextDashboard(ManageDashboardPortlets):
    
    @property
    def category(self):
        return CONTEXT_CATEGORY

    @property
    def key(self):
        return '/'.join(self.context.getPhysicalPath())

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return '%s/++contextportlets++%s' % (baseUrl, manager.__name__)

    def getAssignmentsForManager(self, manager):
        assignments = getMultiAdapter((self.context, manager), IPortletAssignmentMapping)
        return assignments.values()