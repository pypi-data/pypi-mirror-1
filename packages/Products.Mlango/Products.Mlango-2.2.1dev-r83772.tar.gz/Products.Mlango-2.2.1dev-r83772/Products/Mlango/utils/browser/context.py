from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView

from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.interfaces import IPortletManager
from zope.annotation.interfaces import IAnnotations


class ContextDashboardView(BrowserView):
    """Power the dashboard in context mode.
    """
    
    @memoize
    def empty(self):

        annotations = IAnnotations(self.context)
                
        local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)            
 
        count = 0
        
        if local is not None:
            
            for manager in ['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3', 'plone.dashboard4']:
                localManager = local.get(manager, None)
                if localManager is not None:
                    count += len(localManager.values())

        return count == 0