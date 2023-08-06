from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.browser.editmanager import EditPortletManagerRenderer
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.portlets.utils import unhashPortletInfo
from plone.portlets.constants import GROUP_CATEGORY

from zope.interface import Interface
from ZODB.POSException import ConflictError
from zope.component import adapts, getMultiAdapter, getUtility
from Acquisition import aq_acquire

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app.pagetemplate import ViewPageTemplateFile

from zope.annotation.interfaces import IAnnotations

from interfaces import IMlangoPortletRenderingWrapper
from Products.Mlango.utils.interfaces import IMlangoManager
import logging
import sys

logger = logging.getLogger('mlango')


class MlangoPortletManagerRenderer(ColumnPortletManagerRenderer):
    
    """Render one column of the dashboard. The renderer is actually a 'view', 
       or rather multiadapter on the portlet manager.
    """
    
    template = ViewPageTemplateFile('browser/templates/dashboard-column.pt')
   
    
    def getNumberOfColumns(self):

        """ Return the number of columns for the dashboard. This should really
            be set through the tool
        """

        return getUtility(IMlangoManager).columns


    @property
    def columnName(self):
        """ Return column manager name """

        return self.manager.__name__


    def safe_render(self, portlet_renderer, portlet_id):
        """ Find the annotations for the given portlet renderer, and wrap in
            our specific mlango renderer.
        """
        try:
            info = unhashPortletInfo(portlet_id)
            assignments = assignment_mapping_from_key(self.context, 
                info['manager'], info['category'], info['key'])

            assignment = assignments[info['name']]
            annotations = IAnnotations(assignment)
            
            wrapper = getMultiAdapter((portlet_renderer, annotations), IMlangoPortletRenderingWrapper)
            wrapper.id = portlet_id
            wrapper.title = assignment.title
            
            if info['category'] == GROUP_CATEGORY:
                wrapper.isFixed = True
            
            return wrapper.render()
        except ConflictError:
            raise
        except Exception:
            logger.exception('Error while rendering %r' % (self,))
            logger.exception("Error: %s" % str(sys.exc_info()))
            return self.error_message()

        
class MlangoEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for the dashboard
    """

    def addable_portlets(self):
        
        addable = EditPortletManagerRenderer.addable_portlets(self)
        
        if not getUtility(IMlangoManager).filter_portlets:
            
            return addable
        
        allowed = getUtility(IMlangoManager).allow_portlets
        
        return [p for p in addable if p.get('title', None) in allowed]
