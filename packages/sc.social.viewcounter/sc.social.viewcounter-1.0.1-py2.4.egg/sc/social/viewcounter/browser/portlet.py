from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import get_language

from Products.CMFCore.utils import getToolByName

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sc.social.viewcounter import MessageFactory as _

class IViewCounterPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items per list'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)
                       
    showLastHour = schema.Bool(
            title=_(u"Display last hour's top contents."),
            description=_(u"If selected the most accessed content from the last hour will be shown."),
            default=False,
            required=False)
    
    showLastDay = schema.Bool(
            title=_(u"Display last day's top contents."),
            description=_(u"If selected the most accessed content from the last day will be shown."),
            default=True,
            required=False)
    
    showLastWeek = schema.Bool(
            title=_(u"Display last week's top contents."),
            description=_(u"If selected the most accessed content from the last week will be shown."),
            default=False,
            required=False)
    
    showLastMonth = schema.Bool(
            title=_(u"Display last month's top contents."),
            description=_(u"If selected the most accessed content from the last month will be shown."),
            default=False,
            required=False)
    
class Assignment(base.Assignment):
    implements(IViewCounterPortlet)

    def __init__(self, 
                 count=5,
                 showLastHour=True, 
                 showLastDay=False,
                 showLastWeek=False,
                 showLastMonth=False):
        self.count = count
        self.showLastHour = showLastHour
        self.showLastDay = showLastDay
        self.showLastWeek = showLastWeek
        self.showLastMonth = showLastMonth
    
    @property
    def title(self):
        return _(u"Most Accessed")
    
    
def _render_cachekey(fun, self):
    fingerprint = ''.join([d[0] for d in self._data()])
    return "".join((
              getToolByName(aq_inner(self.context), 'portal_url')(),
              get_language(aq_inner(self.context), self.request),
              str(self.anonymous),
              self.manager.__name__,
              self.data.__name__,
              fingerprint))
    

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.reports = context.restrictedTraverse('@@vc_reports')
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
    
    
    @property
    def available(self):
        return 1
    
    def options(self):
        listOptions = []
        data = self.viewcounter()
        if self.data.showLastHour and data.get('lastHour',None):
            listOptions.append(('lastHour',_(u"Last Hour")))
        if self.data.showLastDay and data.get('lastDay',None):
            listOptions.append(('lastDay',_(u"Last Day")))
        if self.data.showLastWeek and data.get('lastWeek',None):
            listOptions.append(('lastWeek',_(u"Last Week")))
        if self.data.showLastMonth and data.get('lastMonth',None):
            listOptions.append(('lastMonth',_(u"Last Month")))
        return listOptions
    
    def viewcounter(self):
        return self._data()
    
    @memoize
    def _data(self):
        count = self.data.count
        lastHour = tuple(self.reports.viewsLastHour()[:count])
        lastDay = tuple(self.reports.viewsLastDay()[:count])
        lastWeek = tuple(self.reports.viewsLastWeek()[:count])
        lastMonth = tuple(self.reports.viewsLastMonth()[:count])
        
        return {'lastHour':lastHour, 
                'lastDay':lastDay,
                'lastWeek':lastWeek,
                'lastMonth':lastMonth,}


class AddForm(base.AddForm):
    form_fields = form.Fields(IViewCounterPortlet)
    label = _(u"Add a Most Accessed Contents Portlet")
    description = _(u"This portlet displays the list of most accessed content.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          showLastHour=data.get('showLastHour', True), 
                          showLastDay=data.get('showLastDay', False),
                          showLastWeek=data.get('showLastWeek', False),
                          showLastMonth=data.get('showLastMonth', False))

class EditForm(base.EditForm):
    form_fields = form.Fields(IViewCounterPortlet)
    label = _(u"Edit Most Accessed Contents Portlet")
    description = _(u"This portlet displays the list of most accessed content.")
