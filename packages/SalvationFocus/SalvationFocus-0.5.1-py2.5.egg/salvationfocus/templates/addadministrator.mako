<%inherit file="headerfooter.mako" />
<%namespace file="util.mako" import="form_field" />

${h.form(h.url(controller='administrator', action='add'), method='post')}

${form_field('login_name', 'Login Name', False, c.form_result, c.form_errors)}
${form_field('password', 'Password', True, c.form_result, c.form_errors)}
${form_field('password_confirm', 'Confirm Password', True, c.form_result, c.form_errors)}
${form_field('email', 'Email', False, c.form_result, c.form_errors)}

<label for="commit"></label>
${h.submit('Add Administrator')}
${h.end_form()}