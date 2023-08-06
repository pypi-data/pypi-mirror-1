from Products.CMFPlone.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase

class ViewCounterViewlet(ViewletBase):
    """A simple viewlet which renders an image used to track users
    """
    
    def render(self):
        marker = '<!-- viewcounter -->'
        if self.isEnabled():
            self.context.restrictedTraverse('@@vc_view')()
            return marker
        else:
            return u''
        
    
    def isEnabled(self):
        context = self.context
        # Available views for this content
        aViews = [name for (name,title) in context.getAvailableLayouts()]
        # Only count page views if the user is **really* viewing the content
        # (ignores edit views, share views and other browser views)
        
        if self._currentView() not in aViews:
            return None
        try:
            portal_type = context.portal_type
        except AttributeError:
            return False
        self._pp = getToolByName(context,'portal_properties',None)
        if hasattr(self._pp,'sc_social_viewcounter'):
            blacklisted_types = list(self._pp.sc_social_viewcounter.getProperty("blacklisted_types") or []) + ['Discussion Item',]
            valid_wf_states = list(self._pp.sc_social_viewcounter.getProperty("valid_wf_states") or [])
        else:
            blacklisted_types = []
            valid_wf_states = []
        wt = getToolByName(context,'portal_workflow',None)
        wf_state = wt.getInfoFor(context,'review_state','')
        return (not(portal_type in blacklisted_types) and (wf_state in valid_wf_states))
    

    def _currentView(self):
        request = self.request
        if 'PUBLISHED' in request.keys():
            cur_view =  getattr(request['PUBLISHED'], '__name__', None) or getattr(request['PUBLISHED'].view, '__name__', None)
            return cur_view
