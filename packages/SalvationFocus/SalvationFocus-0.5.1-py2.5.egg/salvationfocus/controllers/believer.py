import logging

from salvationfocus.lib.base import *
from salvationfocus.model.Believer import Believer

log = logging.getLogger(__name__)

class BelieverController(BaseController):
    
    requires_auth = True
    
    def list(self):
        
        c.title = 'believer'
        c.headers = ['Name', 'Date Entered', 'Last Viewed',
                        'Times Viewed', 'Date Answered']
            
        try:
            c.begin = int(request.params['begin'])
        except:
            c.begin = 0
            
            
        c.total = Session.query(Believer).count()
        
        if c.begin >= c.total:
            c.begin = 0
        
        c.end = c.begin + Session.query(Believer
                                        )[c.begin:c.begin + 20].count()
            
        c.list = Session.query(Believer)[c.begin:c.end]
            
        return render('/bellist.mako')
