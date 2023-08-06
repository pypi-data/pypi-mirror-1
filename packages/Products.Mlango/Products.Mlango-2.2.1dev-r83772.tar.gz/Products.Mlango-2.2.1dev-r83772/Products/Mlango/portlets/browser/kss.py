from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.app.container.interfaces import INameChooser
from zope.annotation.interfaces import IAnnotations

from Acquisition import aq_inner

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base

from plone.portlets.interfaces import IPortletManager, IPortletManagerRenderer
from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.interfaces import IPortletPermissionChecker

import logging
logger = logging.getLogger('mlango')


class PortletManagerKSS(base):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)


    def move_portlet(self, portlethash, source_manager, target_manager, position):
        """ Move the portlet from one view to the other, taking into account the
            new position
        """
        
        info = unhashPortletInfo(portlethash)
        
        tgt_assignments = assignment_mapping_from_key(self.context, 
                                                      target_manager.replace('-', '.'), info['category'], info['key'])            
        IPortletPermissionChecker(tgt_assignments.__of__(aq_inner(self.context)))()

        name = info['name']
        
        # Different manager? Than  delete from source manager
        #
        if source_manager != target_manager:
            src_assignments = assignment_mapping_from_key(self.context, 
                                                source_manager.replace('-', '.'), info['category'], info['key'])            
            assignment = src_assignments.get(info['name'])
            
            del src_assignments[info['name']]
            name = self.add_portlet(tgt_assignments, assignment)

        # Now just change (or redo) order
        #
        keys = list(tgt_assignments.keys())
        if name in keys:
            idx = keys.index(name)
            del keys[idx]
        keys.insert(int(position), name)
        
        tgt_assignments.updateOrder(keys)
        
        return ""

    
    def add_portlet(self, manager, content):
        
        chooser = INameChooser(manager)
        name = chooser.chooseName(None, content)
        manager[name] = content
        
        return name

    
    def delete_portlet(self, portlethash, viewname):

        #logger.info("Incoming request to delete %s from %s" % (portlethash, viewname))
        
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        del assignments[info['name']]
        
        return self._render_column(info, viewname)

    
    def toggle_portlet(self, portlethash, viewname):
        """ Toggle portlet content
        """

        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        assignment = assignments.get(info['name'], None)

        if not assignment:
            raise "No assignment found for %s" % info['name']

        props = IAnnotations(assignment)

        if props.get('minimized', False):
            props['minimized'] = False
        else:
            props['minimized'] = True
            
        return ""


    def _render_column(self, info, view_name):
        """ Render a column separately, to enable Ajax style re-rendering for a
            column within the dashboard.
        """
        #logger.info("Incoming request to render %s for manager %s" % (view_name, info['manager']))
        
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#%s' % info['manager'].replace('.', '-'))
        
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        view = getMultiAdapter((context, request), name=view_name)
        manager = getUtility(IPortletManager, name=info['manager'])
        
        request['key'] = info['key']
        
        request['viewname'] = view_name
        renderer = getMultiAdapter((context, request, view, manager,), IPortletManagerRenderer)
        renderer.update()
        ksscore.replaceHTML(selector, renderer.__of__(context).render())
        return self.render()
