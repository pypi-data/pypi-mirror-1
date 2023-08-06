# -*- coding: utf-8 -*-

from zope.interface import Interface


class IMlangoPortletRenderingWrapper(Interface):
    """ Interface for portlet wrapper
    """    
    
    def render(self, portlet_renderer):
        
        """ Render the portlet by it's renderer, adding the Mlango wrap """
