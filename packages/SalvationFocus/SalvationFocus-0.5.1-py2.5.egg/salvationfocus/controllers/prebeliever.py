import logging
import formencode

from salvationfocus.lib.base import *
from salvationfocus.model.Prebeliever import Prebeliever
from salvationfocus.model.Submitter import Submitter
from salvationfocus.model.Believer import Believer
from salvationfocus.model.form import AddPrebelieverForm, EditPrebelieverForm

from datetime import datetime

log = logging.getLogger(__name__)

class PrebelieverController(BaseController):
    
    requires_auth = True
    
    def add(self):
        
        c.submitters = Session.query(Submitter).all()
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            return render('/addprebeliever.mako')
        
        
        # if there are request.params, then validate it
        # if it validates, give a message saying so and re-show this
        # otherwise, re-show this with the error messages
        schema = AddPrebelieverForm()
        
        try:
            form_result = schema.to_python(request.params)
            
            # add the prebeliever to the db
            pre = Prebeliever()
            pre.first_name = form_result.get('first_name').lower()
            pre.last_name = form_result.get('last_name').lower()
            pre.date_entered = datetime.now()
            pre.submitter_id = form_result.get('submitter_id')
            
            Session.save(pre)
            Session.commit()
            
        except formencode.validators.Invalid, error:
            c.form_result = error.value
            c.form_errors = error.error_dict or {}
            
            # check for chained_validators, otherwise the error
            # message will not be shown
            if c.form_errors.get('form', '') is not '':
                c.message = 'First and last name must be unique.'
        else:
            c.message = 'Prebeliever added successfully.'
            
        return render('/addprebeliever.mako')
    
    def edit(self, id):
        
        c.submitters = Session.query(Submitter).all()
        
        # if there are no request.params, then it is being viewed for the
        # first time. This just skips validation and extra error messages
        # that should not be there yet.
        if len(request.params) == 0:
            
            # check that this prebeliever exists, if so display all the values
            # if not, return an error message
            pre = Session.query(Prebeliever).filter_by(id=id).first()
        
            if pre:
                c.form_result = {}
                c.form_result['first_name'] = pre.first_name
                c.form_result['last_name'] = pre.last_name
                c.form_result['submitter_id'] = pre.submitter_id
            
                return render('/editprebeliever.mako')
            else:
                session['message'] = "That prebeliever could not be found."
                session.save()
                
                return redirect_to(h.url_for(controller='prebeliever',
                                             action='list', id=None))
            
        else:
            # if there are request.params, then validate it
            # if it validates, give a message saying so and re-show this
            # otherwise, re-show this with the error messages
            schema = EditPrebelieverForm()
            
            try:
                form_result = schema.to_python(request.params)
                
                # add the prebeliever to the db
                pre = Session.query(Prebeliever).filter_by(id=id).first()
                pre.first_name = form_result.get('first_name').lower()
                pre.last_name = form_result.get('last_name').lower()
                pre.submitter_id = form_result.get('submitter_id')
                
                Session.commit()
                
            except formencode.validators.Invalid, error:
                c.form_result = error.value
                c.form_errors = error.error_dict or {}
                
                return render('/editprebeliever.mako')
            else:
                session['message'] = 'Prebeliever edited successfully.'
                session.save()
                
            return redirect_to(h.url_for(controller='prebeliever',
                                             action='list', id=None))
    
    def delete(self, id):
        pre = Session.query(Prebeliever).filter_by(id=id).first()
        
        if pre:
            Session.delete(pre)
            Session.commit()
            
            #this is the http session, not the database session
            session['message'] = pre.first_name + " " + \
                                    pre.last_name + \
                                    " has been deleted."
            session.save()
        else:
            session['message'] = 'Could not find prebeliever in the database.'
            session.save()
            
        return redirect_to(h.url_for(controller='prebeliever',
                                             action='list', id=None))
    
    def list(self):
        
        c.title = 'prebeliever'
        c.headers = ['Name', 'Date Entered', 'Last Viewed',
                        'Times Viewed', 'Submitter', 'Edit', 'Believer']
            
        try:
            c.begin = int(request.params['begin'])
        except:
            c.begin = 0
            
            
        c.total = Session.query(Prebeliever).count()
        
        if c.begin >= c.total:
            c.begin = 0
        
        c.end = c.begin + Session.query(Prebeliever
                                        )[c.begin:c.begin + 20].count()
            
        c.list = Session.query(Prebeliever)[c.begin:c.end]
            
        return render('/prelist.mako')
    
    
    
    def saved(self, id):
        
        pre = Session.query(Prebeliever).filter_by(id=id).first()
        
        if pre:
            bel = Believer()
            
            bel.first_name = pre.first_name
            bel.last_name = pre.last_name
            bel.date_entered = pre.date_entered
            bel.last_viewed = pre.last_viewed
            bel.times_viewed = pre.times_viewed
            bel.submitter_id = pre.submitter_id
            bel.date_answered = datetime.now()
            
            Session.save(bel)
            Session.delete(pre)
            
            Session.commit()
            
            session['message'] = bel.first_name.capitalize() + " " + \
                                    bel.last_name.capitalize() + \
                                    " has become a believer."
            session.save()
            
        else:
            session['message'] = "Could not find prebeliever"
            session.save()
            
        return redirect_to(h.url_for(controller='prebeliever',
                                             action='list', id=None))
