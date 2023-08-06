<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

${h.form(h.url(controller='prebeliever', action='edit'), method='post')}

${form_field('first_name', 'First Name', False, c.form_result, c.form_errors)}
${form_field('last_name', 'Last Name', False, c.form_result, c.form_errors)}

<label for="submitter_id" >Submitter: </label>
<select id="submitter_id" name="submitter_id" >
% for sub in c.submitters:
    % if 'submitter_id' in c.form_result and int(c.form_result['submitter_id']) == sub.id:
        <option value=${sub.id} selected>${sub.first_name.capitalize()} ${sub.last_name.capitalize()}</option>
    % else:
        <option value=${sub.id}>${sub.first_name.capitalize()} ${sub.last_name.capitalize()}</option>
    % endif
% endfor
</select><br />

<label for="commit"></label>
${h.submit('Edit Prebeliever')}
${h.end_form()}<br />

<a href="${h.url_for(controller='prebeliever', action='delete')}" >Delete this prebeliever</a>