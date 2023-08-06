from zope.app.pagetemplate import ViewPageTemplateFile


class MlangoPortletRenderingWrapper:
    """
      We wrap the IPortletRenderer in the Mlango renderer, together with the
      assignment annotations, so we can add some extra HTML here and there...
    """

    render = ViewPageTemplateFile('browser/templates/portlet.pt')

    
    def __init__(self, renderer, annotations):

        """ Initialize taking the wrapped renderer  as argument """
        
        self.renderer = renderer
        self.context = renderer.context
        self.request = renderer.request
        self.view = renderer.view
        self.__parent__ = renderer.view
        self.manager = renderer.manager
        self.data = renderer.data
        self.id = None
        self.title = None
        self.annotations = annotations

        self.hasHelp = False
        self.isFixed = False
        self.icon = "mlangodashboard_icon.png"
        
        
    def render_portlet(self):
        """ Render wrapped portlet
        """
        
        return self.renderer.render()

    @property
    def title(self):
        
        return self.title
        
    @property
    def isMinimized(self):
        
        return self.annotations.get('minimized', False)

    @property
    def isFixed(self):
        
        return self.isFixed or self.annotations.get('fixed', False)

    
    def getHelp(self):
        
        return "HELP"