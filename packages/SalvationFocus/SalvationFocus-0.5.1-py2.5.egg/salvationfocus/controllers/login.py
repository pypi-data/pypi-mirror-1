import logging
import hashlib

from salvationfocus.lib.base import *
from salvationfocus.model.Administrator import Administrator

log = logging.getLogger(__name__)

class LoginController(BaseController):

    def index(self):
        return render('/login.mako')
    
    
    
    def submit(self):
        
        form_username = str(request.params.get('login_name'))
        form_password = str(request.params.get('password'))
        
        sql_session = model.Session()
        
        pass_hash = hashlib.sha256(form_password).hexdigest()
        
        db_user = sql_session.query(Administrator
                        ).filter_by(login_name=form_username
                        ).filter_by(password_hash=pass_hash
                        ).first()
        
        sql_session.close()
        
        if db_user == None:
            return render('/login.mako')
        
        session['user'] = form_username
        session.save()
        
        if session.get('path_before_login'):
            redirect_to(session['path_before_login'])
        else:
            return redirect_to(h.url_for(controller='main'))
        
        
        
    def logout(self, *args):
        if 'user' in session:
            del session['user']
            
        session['message'] = 'You\'ve been logged out successfully.'
        session.save()
        
        return redirect_to(h.url_for(controller='main'))
    
    
    def remind(self):
        session['message'] = 'This is not implemented yet. Sorry.'
        session.save()
        return redirect_to(h.url_for(controller='login'))
    #
    #
    #def get_password(self):
    #    
    #    form_username = str(request.params.get('login_name'))
    #    
    #    #we only have the password hash, how should we handle this???
    #    
    #    #for now, redirect to login page
    #    return redirect_to(h.url_for(controller='login'))