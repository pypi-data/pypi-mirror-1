<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

${h.form(h.url(controller='prebeliever', action='add'), method='post')}

${form_field('first_name', 'First Name', False, c.form_result, c.form_errors)}
${form_field('last_name', 'Last Name', False, c.form_result, c.form_errors)}

<label for="submitter_id" >Submitter: </label>
<select id="submitter_id" name="submitter_id" >
% for sub in c.submitters:
    % if i == 0:
        <option value=${sub.id} selected>${sub.first_name.capitalize()} ${sub.last_name.capitalize()}</option>
    % else:
        <option value=${sub.id}>${sub.first_name.capitalize()} ${sub.last_name.capitalize()}</option>
    % endif
% endfor
</select><br />

<label for="commit"></label>
${h.submit('Add Prebeliever')}
${h.end_form()}