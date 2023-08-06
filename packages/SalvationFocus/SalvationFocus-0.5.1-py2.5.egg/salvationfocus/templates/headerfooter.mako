<%inherit file="base.mako" />

<div id="header">
<a href="${h.url_for(controller='main')}">Main</a><br />
<a href="${h.url_for(controller='login', action='logout')}">Logout ${session['user']}</a>
</div>

% if c.message:
    <p><div class="message">${c.message}</div></p>
% endif

% if 'message' in session:
    <p><div class="message">${session['message']}</div></p>
    <%
        del session['message']
        session.save()
    %>
% endif

<div class="main">
${next.body()}
</div>

<div id="footer">
Salvation Focus copyright 2007 geekforGod Consulting
</div>