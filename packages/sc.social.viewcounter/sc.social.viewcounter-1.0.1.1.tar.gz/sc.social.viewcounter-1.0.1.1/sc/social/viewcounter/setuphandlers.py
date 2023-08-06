import os
from z3c.saconfig import named_scoped_session
from sc.social.viewcounter.pageview import Base
from sc.social.viewcounter.pageview import SCOPED_SESSION_NAME
import logging
logger = logging.getLogger('sc.social.viewcounter: setuphandlers')

Session = named_scoped_session(SCOPED_SESSION_NAME)

def isNotOurProfile(context):
    return context.readDataFile("sc.social.viewcounter.txt") is None

def create_tables(context):
    '''Called at profile import time to create necessary tables
    '''
    if isNotOurProfile(context):return
    Base.metadata.create_all(bind=Session.bind)