# -*- charset:utf-8 -*-

from zope.interface import implements
from datetime import datetime as dt

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from z3c.saconfig import named_scoped_session

from sc.social.viewcounter.interfaces import IPageView
from sc.social.viewcounter import MessageFactory as _


Base = declarative_base()

SCOPED_SESSION_NAME = 'sc.social.viewcounter.db'

session =  named_scoped_session(SCOPED_SESSION_NAME)

class PageView(Base):
    """A single page view -- when a user access one content in our site"""
    
    implements(IPageView)
    
    __tablename__ = 'viewcounter_pageviews'
    __table_args__ = {'mysql_engine':'InnoDB','mysql_charset':'utf8'}
    
    id = sa.Column(sa.Integer, primary_key=True)
    object_uid = sa.Column(sa.String(32),nullable=False,index=True)
    object_path = sa.Column(sa.String(512),nullable=False,index=True)
    object_type = sa.Column(sa.String(50),nullable=False,index=True)
    access_datetime = sa.Column(sa.DateTime, nullable=False,index=True)
    user_ip = sa.Column(sa.String(15),nullable=False)
    user_name = sa.Column(sa.String(200),nullable=False)
    
    def __init__(self, object_uid,object_path,object_type,user_ip,user_name):
        self.object_uid = object_uid
        self.object_path = object_path
        self.object_type = object_type
        self.access_datetime = dt.now()
        self.user_ip = user_ip
        self.user_name = user_name
    
    def __repr__(self):
       return "<PageView ('%s','%s')>" % (self.object_path,
                                          self.user_ip,
                                          self.access_datetime.strftime('%Y/%m/%d %H:%M:%S'))
    


    