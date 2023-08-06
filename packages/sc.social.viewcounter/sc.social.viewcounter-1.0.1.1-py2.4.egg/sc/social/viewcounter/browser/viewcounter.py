# -*- coding:utf-8 -*-
from datetime import datetime
from datetime import timedelta
from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from Acquisition import aq_inner
from Products.CMFPlone.utils import getToolByName,log

from sqlalchemy import sql, orm
from sqlalchemy import and_
from sqlalchemy import func 
from sqlalchemy.sql.expression import desc

from plone.memoize.instance import memoize

from sc.social.viewcounter.pageview import session
from sc.social.viewcounter.pageview import PageView


class PageViewBV(BrowserView):
    """ Base BrowserView to PageView
    """
    session = None
    
    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        self.session = session()
        super(PageViewBV, self).__init__(context, request)
    
    def __call__(self, **kw):
        """ Create a new pageview
            Returns the pageview
        """
        session = self.session
        context = self.context
        request = self.request
        mt = getToolByName(context,'portal_membership')
        
        if mt.isAnonymousUser(): # the user has not logged in
            userid = 'Anonymous'
        else:
            member = mt.getAuthenticatedMember()
            userid = member.getUserName()
        if hasattr(context,'UID'):
            # Creates a new PageView object
            object_uid = context.UID()
            object_path = '/'.join(context.getPhysicalPath())
            object_type = context.portal_type
            user_ip = request.get('X-Forwarded-For',request.get('REMOTE_ADDR'))
            user_name = userid
            
            pv = PageView(object_uid,object_path,object_type,user_ip,user_name)
            # Adds to session and commits transaction
            session.add(pv)
    


class Reports(BrowserView):
    
    session = None
    
    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        self.session = session()
        self.ct = getToolByName(self.context,'portal_catalog')
        self._pp = getToolByName(self.context,'portal_properties',None)
        if hasattr(self._pp,'sc_social_viewcounter'):
            blacklisted_types = list(self._pp.sc_social_viewcounter.getProperty("blacklisted_types") or []) + ['Discussion Item',]
        else:
            blacklisted_types = []
        self.blacklisted_types = blacklisted_types
        super(Reports, self).__init__(context, request)
    
    def _reportPageViews(self,dateRange,portal_type='',path=''):
        session = self.session
        where=[]
        where.append(PageView.access_datetime.between(*dateRange))
        if portal_type:
            where.append(PageView.object_type==portal_type)
        if path:
            where.append(PageView.object_path==path)
        where = and_(*where)
        pvs = session.query(func.count('*'),PageView.object_uid).filter(where).order_by(desc(func.count('*'))).group_by(PageView.object_uid)
        listPvs = pvs.all()
        uids = [uid for (pv,uid) in pvs]
        dictByUIDs = self.dictByUIDs(uids)
        return [(uid,dictByUIDs[uid].get('Title'),dictByUIDs[uid].get('url'),pv) for (pv,uid) in listPvs if dictByUIDs.get(uid,None)]
    
    def dictByUIDs(self,uids):
        ct = self.ct
        blacklisted = self.blacklisted_types
        results = ct.unrestrictedSearchResults(UID={'query':uids})
        dictByUIDs = dict([(brain.UID,{'Title':brain.Title,
                                      'path':brain.getPath(),
                                      'url':brain.getURL(),
                                      'portal_type':brain.portal_type}) \
                                      for brain in results \
                                      if brain.portal_type not in blacklisted])
        return dictByUIDs
        
    
    @property
    def lastHour(self):
        now = datetime.now()
        delta = timedelta(0,3600)
        base_dt = (now - delta)
        start = datetime(base_dt.year,
                         base_dt.month,
                         base_dt.day,
                         base_dt.hour,
                         0,
                         0,
                        )
        end = datetime(base_dt.year,
                       base_dt.month,
                       base_dt.day,
                       base_dt.hour,
                       59,
                       59,
                       )
        return (start,end)
    
    @property
    def lastDay(self):
        now = datetime.now()
        delta = timedelta(1,0)
        base_dt = (now - delta)
        start = datetime(base_dt.year,
                         base_dt.month,
                         base_dt.day,
                         0,
                         0,
                         0,
                        )
        end = datetime(base_dt.year,
                       base_dt.month,
                       base_dt.day,
                       23,
                       59,
                       59,
                       )
        return (start,end)
    
    @property
    def lastWeek(self):
        now = datetime.now()
        weekday = now.weekday()
        delta = timedelta(7+weekday,0)
        base_dt = (now - delta)
        start = datetime(base_dt.year,
                         base_dt.month,
                         base_dt.day,
                         0,
                         0,
                         0,
                        )
        delta = timedelta(1+weekday,0)
        base_dt = (now - delta)        
        end = datetime(base_dt.year,
                       base_dt.month,
                       base_dt.day,
                       23,
                       59,
                       59,
                       )
        return (start,end)
        
    
    @property
    def lastMonth(self):
        now = datetime.now()
        day = now.day
        delta = timedelta(day,0)
        base_dt = (now - delta)
        start = datetime(base_dt.year,
                         base_dt.month,
                         1,
                         0,
                         0,
                         0,
                        )
        base_dt = (now - delta)        
        end = datetime(base_dt.year,
                       base_dt.month,
                       base_dt.day,
                       23,
                       59,
                       59,
                       )
        return (start,end)
        
    
    @property
    def allTime(self):
        now = datetime.now()
        base_dt = now
        start = datetime(2000,
                         1,
                         1,
                         0,
                         0,
                         0,
                        )
        end = base_dt
        return (start,end)
        
    
    @property
    def lastYear(self):
        now = datetime.now()
        base_dt = now
        start = datetime(base_dt.year-1,
                         1,
                         1,
                         0,
                         0,
                         0,
                        )
        delta = timedelta(1+weekday,0)
        base_dt = (now - delta)        
        end = datetime(base_dt.year-1,
                       12,
                       31,
                       23,
                       59,
                       59,
                       )
        return (start,end)
        
    
    def viewsLastHour(self):
        range = self.lastHour
        return self._reportPageViews(range)
    
    def viewsLastDay(self):
        range = self.lastDay
        return self._reportPageViews(range)
    
    def viewsLastWeek(self):
        range = self.lastWeek
        return self._reportPageViews(range)
    
    def viewsLastMonth(self):
        range = self.lastMonth
        return self._reportPageViews(range)
    
    def viewsLastYear(self):
        range = self.lastYear
        return self._reportPageViews(range)
    
    def viewsAllTime(self):
        range = self.allTime
        return self._reportPageViews(range)
    


       