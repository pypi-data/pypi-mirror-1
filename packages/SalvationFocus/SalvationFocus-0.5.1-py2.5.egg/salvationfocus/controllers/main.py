import logging

from salvationfocus.lib.base import *

log = logging.getLogger(__name__)

class MainController(BaseController):
    
    requires_auth = True

    def index(self):
        return render('/main.mako')
