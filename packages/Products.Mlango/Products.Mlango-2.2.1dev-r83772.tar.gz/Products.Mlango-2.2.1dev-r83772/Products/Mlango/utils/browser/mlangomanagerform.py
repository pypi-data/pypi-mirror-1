from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.component import getUtilitiesFor
from plone.app.controlpanel.form import ControlPanelForm
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.form.browser import RadioWidget, MultiSelectWidget
from plone.portlets.interfaces import IPortletType
from Products.Mlango.utils.interfaces import IMlangoManager

_ = MessageFactory('mlango')


def ColumnWidget(field, request):
    vocabulary = SimpleVocabulary.fromValues([3, 4])
    return RadioWidget(field, vocabulary, request)


def AllowPortletsWidget(field, request):
    
    # Collect portlet id and descriptions
    portlets = [(p[1].title, p[1].title) for p in getUtilitiesFor(IPortletType)]
    
    vocabulary = SimpleVocabulary.fromItems(portlets)
    return MultiSelectWidget(field, vocabulary, request)


class MlangoManagerForm(ControlPanelForm):
    
    """ Mlango configlet form
    """

    form_fields = form.Fields(IMlangoManager)
    form_fields['columns'].custom_widget = ColumnWidget
    form_fields['allow_portlets'].custom_widget = AllowPortletsWidget
    
    label = _(u"heading_mlango_settings", default="Mlango Settings")
    description = _(u"description_mlango_settings",
                    default="Settings related to Mlango")
    form_name = _(u"heading_mlango_settings", default="Mlango Settings")
