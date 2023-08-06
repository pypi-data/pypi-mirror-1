from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.compress import xhtml_compress

class ViewletFeeder:
    """ This Zope3 view enables viewlets easily to return show their entire frame (+content),
    or just their content! Down side is that the "Classic Viewlet" (using macro's of old portlets),
    is unable to work in such a context due to lack of 'here' or 'here_url'.
    """
    def feeder(self):
        """ Retrieve the template from the viewlet (same for all),
        and then use xhtml_compress to view it.
        """
        template = self.context.returnTemplate()
        return xhtml_compress(template())
    
    def contentfeeder(self):
        """ Retrieve the contenttemplate from the viewlet (unique for each content type of viewlet),
        and then use xhtml_compress to view it.
        This view is called in the template to draw the content of a viewlet.
        """
        template = self.context.returnContentTemplate()
        return xhtml_compress(template())
