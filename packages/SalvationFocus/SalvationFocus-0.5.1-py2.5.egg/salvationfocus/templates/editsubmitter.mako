<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

${h.form(h.url(controller='submitter', action='edit'), method='post')}

${form_field('first_name', 'First Name', False, c.form_result, c.form_errors)}
${form_field('last_name', 'Last Name', False, c.form_result, c.form_errors)}
${form_field('phone', 'Phone', False, c.form_result, c.form_errors)}
${form_field('email', 'Email', False, c.form_result, c.form_errors)}

<label for="commit"></label>
${h.submit('Edit Submitter')}
${h.end_form()}<br />

<a href="${h.url_for(controller='submitter', action='delete')}" >Delete this submitter</a>