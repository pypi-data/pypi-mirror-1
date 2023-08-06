from zope.interface import Interface
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class IMlangoManager(Interface):
    """ Marker interface
    """

    columns = schema.Int(title=_(u'label_columns',
                            default=u'Number of columns'),
                    description=_(u"help_columns",
                                  default=u"The number of columns to be used on the dashboard"),
                    default=4,
                    required=True)
    
    filter_portlets = schema.Bool(title=_(u'label_filter_portlets', default=u'Filter portlets'),
                                  description=_(u'description_filter_portlets', default=u'Switch to enable filter on available portlets for users'),
                                  default=False,
                                  required=False
                                  )
    
    allow_portlets = schema.List(title=_(u'label_allow_portlets', default=u'Allow these porlets'),
                                 description=_(u'description_allow_portlets', default=u'This setting only has effect when Filter portlets is switched on'),
                                 required=False
                                 )
    
    
class IManageGroupDashboard(Interface):
    """ Marker
    """

class IManageContextDashboard(Interface):
    """ Marker
    """