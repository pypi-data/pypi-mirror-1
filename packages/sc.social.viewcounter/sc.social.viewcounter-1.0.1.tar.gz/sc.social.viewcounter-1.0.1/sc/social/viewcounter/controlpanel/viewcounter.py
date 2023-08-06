from zope.schema import Int
from zope.schema import TextLine
from zope.schema import Tuple
from zope.schema import Choice
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from zope.formlib.form import FormFields
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiSelectTupleWidget

from sc.social.viewcounter import MessageFactory as _


class IViewCounterSchema(Interface):
    
    blacklisted_types = Tuple(
        title=_(u'Content types blacklist'),
        description=_(u'help_blacklisted_types',
            default=u"Please check any blacklisted content type -- type not to be listed on portlets and viewlets.",
        ),
        missing_value=set(),
        value_type=Choice(vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"),
    )
    
    valid_wf_states = Tuple(
        title=_(u'Valid workflow states'),
        description=_(u'help_valid_wf_statess',
            default=u"Please inform workflow states that will be shown on rankings.",
        ),
        missing_value=set(),
        value_type=Choice(vocabulary="plone.app.vocabularies.WorkflowStates"),
    )

class ViewCounterControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(IViewCounterSchema)
    
    def __init__(self, context):
        super(ViewCounterControlPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(context, 'portal_properties')
        self.context = portal_properties.sc_social_viewcounter
    
    
    blacklisted_types = ProxyFieldProperty(IViewCounterSchema['blacklisted_types'])
    valid_wf_states = ProxyFieldProperty(IViewCounterSchema['valid_wf_states'])
    

class ViewCounterControlPanel(ControlPanelForm):

    form_fields = FormFields(IViewCounterSchema)
    #form_fields['blacklisted_types'].custom_widget = MultiSelectTupleWidget
    
    label = _(u'ViewCounter Settings')
    description = _(u'Settings for sc.social.viewcounter.')
    form_name = _(u'ViewCounter Settings')
