import logging
import formencode

from salvationfocus.lib.base import *
from salvationfocus.model.Submitter import Submitter
from salvationfocus.model.form import AddSubmitterForm, EditSubmitterForm

log = logging.getLogger(__name__)

class SubmitterController(BaseController):
    
    requires_auth = True
    
    def add(self):
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            return render('/addsubmitter.mako')
        
        
        # if there are request.params, then validate it
        # if it validates, give a message saying so and re-show this
        # otherwise, re-show this with the error messages
        schema = AddSubmitterForm()
        
        try:
            form_result = schema.to_python(request.params)
            
            # add the submitter to the db
            sub = Submitter()
            sub.first_name = form_result.get('first_name').lower()
            sub.last_name = form_result.get('last_name').lower()
            sub.phone = form_result.get('phone')
            sub.email = form_result.get('email').lower()
            
            Session.save(sub)
            Session.commit()
            
        except formencode.validators.Invalid, error:
            c.form_result = error.value
            c.form_errors = error.error_dict or {}
            
            # check for chained_validators, otherwise the error
            # message will not be shown
            if c.form_errors.get('form', '') is not '':
                c.message = 'First and last name must be unique.'
        else:
            c.message = 'Submitter added successfully.'
            
        return render('/addsubmitter.mako')
        
        
    def edit(self, id):
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            
            # check that this submitter exists, if so display all the values
            # if not, return an error message
            sub = Session.query(Submitter).filter_by(id=id).first()
        
            if sub:
                c.form_result = {}
                c.form_result['first_name'] = sub.first_name
                c.form_result['last_name'] = sub.last_name
                c.form_result['phone'] = sub.phone
                c.form_result['email'] = sub.email
            
                return render('/editsubmitter.mako')
            else:
                session['message'] = "That submitter could not be found."
                session.save()
                
                return redirect_to(h.url_for(controller='submitter',
                                             action='list', id=None))
            
        else:
            # if there are request.params, then validate it
            # if it validates, give a message saying so and re-show this
            # otherwise, re-show this with the error messages
            schema = EditSubmitterForm()
            
            try:
                form_result = schema.to_python(request.params)
                
                # add the submitter to the db
                sub = Session.query(Submitter).filter_by(id=id).first()
                sub.first_name = form_result.get('first_name').lower()
                sub.last_name = form_result.get('last_name').lower()
                sub.phone = form_result.get('phone')
                sub.email = form_result.get('email').lower()
                
                Session.commit()
                
            except formencode.validators.Invalid, error:
                c.form_result = error.value
                c.form_errors = error.error_dict or {}
                
                return render('/editsubmitter.mako')
            else:
                session['message'] = 'Submitter edited successfully.'
                session.save()
                
            return redirect_to(h.url_for(controller='submitter',
                                             action='list', id=None))
    
    def delete(self, id):
        
        sub = Session.query(Submitter).filter_by(id=id).first()
        
        if sub:
            Session.delete(sub)
            Session.commit()
            
            #this is the http session, not the database session
            session['message'] = sub.first_name + " " + \
                                    sub.last_name + \
                                    " has been deleted."
            session.save()
        else:
            session['message'] = 'Could not find submitter in the database.'
            session.save()
            
        return redirect_to(h.url_for(controller='submitter',
                                             action='list', id=None))
    
    def list(self):
        
        c.title = 'submitter'
        c.headers = ['Name', 'Phone', 'Email', 'Edit']
            
        try:
            c.begin = int(request.params['begin'])
        except:
            c.begin = 0
            
            
        c.total = Session.query(Submitter).count()
        
        if c.begin >= c.total:
            c.begin = 0
        
        c.end = c.begin + Session.query(Submitter
                                        )[c.begin:c.begin + 20].count()
            
        c.list = Session.query(Submitter)[c.begin:c.end]
            
        return render('/sublist.mako')