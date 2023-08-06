import logging
import xmlrpclib
import pylons

from pylons import request
from pylons.controllers import XMLRPCController
from salvationfocus.lib.base import *

from salvationfocus.model import Session
from salvationfocus.model.Prebeliever import Prebeliever

from datetime import datetime


log = logging.getLogger(__name__)

class GetprebelieverController(XMLRPCController):

    def get_prebeliever(self):
        #get prebeliever
        
        session = Session()
        
        #get the first prebeliever that has never been viewed
        #that has been in the database longer than any other
        #prebeliever that has never been viewed
        pre = session.query(Prebeliever
            ).filter_by(last_viewed=None
            ).order_by(Prebeliever.date_entered.asc()
            ).first()
        
        #every prebeliever has been viewed at least once
        #or there are none at all
        if(pre == None):
            #get the prebeliever that has not been viewed in the
            #longest amount of time
            pre = session.query(Prebeliever
                ).order_by(Prebeliever.last_viewed.asc()
                ).first()
            
            #there are no prebelievers at all
            if(pre == None):
                result = {}
                result['error'] = 'No prebelievers'
                session.close()
                return result
        
        #update the last time viewed to now
        #and increase the times viewed by one
        pre.last_viewed = datetime.now()
        
        if pre.times_viewed:
            pre.times_viewed = pre.times_viewed + 1
        else:
            pre.times_viewed = 1
        
        session.commit()
        session.close()
        
        return pre.toDictionary()
