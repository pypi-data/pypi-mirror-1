<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

Current Email: ${c.email}<br />

${h.form(h.url(controller='administrator', action='edit_email'), method='post')}

${form_field('email', 'Email', False, c.form_result, c.form_errors)}

<label for="commit"></label>
${h.submit('Change My Email')}
${h.end_form()}