import logging
import formencode
import hashlib

from salvationfocus.lib.base import *
from salvationfocus.model.Administrator import Administrator
from salvationfocus.model.form import AddAdministratorForm
from salvationfocus.model.form import EditAdministratorPassword
from salvationfocus.model.form import EditAdministratorEmail

log = logging.getLogger(__name__)

class AdministratorController(BaseController):
    
    requires_auth = True
    
    def add(self):
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            return render('/addadministrator.mako')
        
        
        # if there are request.params, then validate it
        # if it validates, give a message saying so and re-show this
        # otherwise, re-show this with the error messages
        schema = AddAdministratorForm()
        
        try:
            form_result = schema.to_python(request.params)
            
            # add the administrator to the db
            ad = Administrator()
            ad.login_name = form_result.get('login_name').lower()
            
            pass_hash = hashlib.sha256(form_result.get('password')).hexdigest()
            
            ad.password_hash = pass_hash
            ad.email = form_result.get('email').lower()
            
            Session.save(ad)
            Session.commit()
            
        except formencode.validators.Invalid, error:
            c.form_result = error.value
            c.form_errors = error.error_dict or {}
            
            # check for chained_validators, otherwise the error
            # message will not be shown
            if c.form_errors.get('form', '') is not '':
                c.message = 'Login name must be unique.'
        else:
            c.message = 'Administrator added successfully.'
            
        return render('/addadministrator.mako')
    
    
    
    def edit_password(self):
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            return render('/edit_password.mako')
        
        
        # if there are request.params, then validate it
        # if it validates, give a message saying so and re-show this
        # otherwise, re-show this with the error messages
        schema = EditAdministratorPassword()
        
        try:
            form_result = schema.to_python(request.params)
            
            # check that the current password hash entered matches
            # the password hash in the database
            c_pass = form_result.get('current_password')
            c_pass_hash = hashlib.sha256(c_pass).hexdigest()
            
            ad = Session.query(Administrator).filter_by(login_name=session['user']).first()
            
            # if so, hash the new value and enter it
            if ad.password_hash == c_pass_hash:
                new_hash = hashlib.sha256(form_result.get('new_password')).hexdigest()
                
                ad.password_hash = new_hash
                
                Session.commit()

            # if not, go back with an error message
            else:
                session['message'] = 'You entered an incorrect current password.'
                session.save()
                
                return render('/edit_password.mako')
            
        except formencode.validators.Invalid, error:
            c.form_result = error.value
            c.form_errors = error.error_dict or {}
            
            return render('/edit_password.mako')
        else:
            session['message'] = 'Your password has been changed.'
            session.save()
            
        return redirect_to(h.url_for(controller='main'))



    def edit_email(self):
        
        ad = Session.query(Administrator).filter_by(login_name=session['user']).first()
        c.email = ad.email
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            return render('/edit_email.mako')
        
        
        # if there are request.params, then validate it
        # if it validates, give a message saying so and re-show this
        # otherwise, re-show this with the error messages
        schema = EditAdministratorEmail()
        
        try:
            form_result = schema.to_python(request.params)
            
            ad.email = form_result.get('email')
                
            Session.commit()
            
        except formencode.validators.Invalid, error:
            c.form_result = error.value
            c.form_errors = error.error_dict or {}
            
            return render('/edit_email.mako')
        else:
            session['message'] = 'Your email address has been changed.'
            session.save()
            
        return redirect_to(h.url_for(controller='main'))
    
    
    
    
    def delete(self, id):
        
        ad = Session.query(Administrator).filter_by(id=id).first()
        
        if ad:
            Session.delete(ad)
            Session.commit()
            
            #this is the http session, not the database session
            session['message'] = ad.login_name + " " + \
                                    " has been deleted."
            session.save()
        else:
            session['message'] = 'Could not find administrator in the database.'
            session.save()
            
        return redirect_to(h.url_for(controller='administrator',
                                             action='list', id=None))
    
    def list(self):
        
        c.title = 'administrator'
        c.headers = ['Login Name', 'Email']
            
        try:
            c.begin = int(request.params['begin'])
        except:
            c.begin = 0
            
            
        c.total = Session.query(Administrator).count()
        
        if c.begin >= c.total:
            c.begin = 0
        
        c.end = c.begin + Session.query(Administrator
                                        )[c.begin:c.begin + 20].count()
            
        c.list = Session.query(Administrator)[c.begin:c.end]
            
        return render('/adlist.mako')
