## create a label and text input field for a form
<%def name="form_field(name, label_text, password=False, form_results=None, form_errors=None)" >
    <label for="${name}"
    
    ## check that form_errors is not None
    ## check that form_errors is not a string, this happens sometimes
    ## with Pylons
    ## it should be a dict, check for the corresponding error message
    ## this is just for convenience to type
    ## % if errors:
    ## instead of
    ## % if form_errors and form_errors is not '' and etc...
    <% errors = False %>
    % if form_errors and form_errors is not '' and form_errors.get(name, '') is not '':
        <% errors = True %>
    % endif
    
    % if errors:
        class="error_label"
    % endif
    
    >${label_text}: </label>
    
    % if form_results and form_results is not '':
        % if password:
            ${h.password_field(name, value=form_results.get(name, ''))}
        % else:
            ${h.text_field(name, value=form_results.get(name, ''))}
        % endif
    % else:
        % if password:
            ${h.password_field(name)}
        % else:
            ${h.text_field(name)}
        % endif
    % endif
    
    % if errors:
        * ${form_errors.get(name, '')}
    % endif
    
    <br />
    
</%def>