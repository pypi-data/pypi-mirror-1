from zope.component import getMultiAdapter, getUtility
from zope.schema.fieldproperty import FieldProperty
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets.browser.manage import ManageDashboardPortlets
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView
from plone.portlets.constants import CONTEXT_CATEGORY

from interfaces import IMlangoManager


def form_adapter(context):
    return getUtility(IMlangoManager, context=context)


class MlangoManager(object):
    """ The MlangoManager enables site wide settings for the user dashboard. The
        manager can set default portlets, and gives admins the means of fixing
        portlets on the user dashboard. The MlangoManager stores the portlet
        settings in the CONTEXT key as annotations on the utility.
    """

    columns = FieldProperty(IMlangoManager['columns'])
    filter_portlets = FieldProperty(IMlangoManager['filter_portlets'])
    allow_portlets = FieldProperty(IMlangoManager['allow_portlets'])


class ManageMlangoDashboard(ManageDashboardPortlets):
    """ This class extends the ManageDashboardPortlets class, so we
        automagically get the edit mode screen for this manager.
        This is achieved with the appropriate edit manager adapting to the
        IManageDashbpardPortlets interface.
    """

    def __init__(self, context, request):
        super(ManageMlangoDashboard, self).__init__(context, request)
        self.request.set('disable_border', True)


    @property
    def category(self):

        return CONTEXT_CATEGORY

    
    @property
    def key(self):

        return 'mlangomanager'

    
    getAssignmentMappingUrl = ManageDashboardPortlets.getAssignmentMappingUrl
    
    
    def getAssignmentsForManager(self, manager):
        assignments = getMultiAdapter((self.context, manager), IPortletAssignmentMapping)
        return assignments.values()
