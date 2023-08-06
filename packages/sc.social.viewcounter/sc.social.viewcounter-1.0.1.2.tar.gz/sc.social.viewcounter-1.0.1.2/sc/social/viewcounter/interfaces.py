# -*- charset:utf-8 -*-

from zope import schema
from zope.interface import Interface

from sc.social.viewcounter import MessageFactory as _

class IPageView(Interface):
    ''' A single page view -- when a user access one content in our site
    '''
    # Object Data
    object_uid = schema.ASCIILine(title=_('Object UID'),
                                  required=True)
    object_path = schema.ASCIILine(title=_('Object path'),
                                   required=True)
    object_type = schema.TextLine(title=_('Portal type'),
                                  required=True)
    # Access data
    access_datetime = schema.Datetime(title=_('Access date'),
                                      required=True,
                                      readonly=True)
    user_ip = schema.TextLine(title=_('User IP address'),
                              required=True)
    username = schema.TextLine(title=_('Username'),
                               required=True)
    

class IReports(Interface):
    ''' Reports interface
    '''
    def viewsLastHour(self):
        pass
    
    def viewsLastDay(self):
        pass
    
    def viewsLastWeek(self):
        pass
    
    def viewsLastMonth(self):
        pass
    
    def viewsLastYear(self):
        pass
    
    def viewsAllTime(self):
        pass
