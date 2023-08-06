from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import Choice, List
from zope.formlib import form

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from atreal.override.sharing import OverrideSharingMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm

class IOverrideSharingSchema(Interface):

    sharing_group_confidential = List(title = _(u"Groups authorized"),
                                      required = False,
                                      default = [],
                                      value_type = Choice(title=_(u"Groups authorized"),
                                                          source="plone.app.vocabularies.Groups"))

class OverrideSharingControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IOverrideSharingSchema)

    def __init__(self, context):
        super(OverrideSharingControlPanelAdapter, self).__init__(context)

    sharing_group_confidential = ProxyFieldProperty(IOverrideSharingSchema['sharing_group_confidential'])
    
class OverrideSharingControlPanel(ControlPanelForm):
    
    form_fields = form.FormFields(IOverrideSharingSchema)
    label = _("OverrideSharing settings")
    description = _("OverrideSharing settings for this site.")
    form_name = _("OverrideSharing settings")
