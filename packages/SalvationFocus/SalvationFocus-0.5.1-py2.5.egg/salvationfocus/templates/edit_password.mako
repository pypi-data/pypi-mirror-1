<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

${h.form(h.url(controller='administrator', action='edit_password'), method='post')}

${form_field('current_password', 'Current Password', True, c.form_result, c.form_errors)}
${form_field('new_password', 'New Password', True, c.form_result, c.form_errors)}
${form_field('confirm_password', 'Confirm New Password', True, c.form_result, c.form_errors)}

<label for="commit"></label>
${h.submit('Change My Password')}
${h.end_form()}