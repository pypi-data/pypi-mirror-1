<%inherit file="base.mako" />

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

<div class="login">
    
    <em>Salvation Focus Administrator</em>
    
    <form action="${h.url_for(controller='login', action='submit')}" method="post">
        <label for="login_name">Login:</label><input type="text" title="Enter your login" name="login_name" id="login_name" value="" /><br />
        <label for="password">Password:</label><input type="password" title="Enter your password" name="password" id="password" value="" /><br />
        <label for="commit"></label><input type="submit" value="Login" /><br />
        <a href="${h.url_for(controller="login", action="remind")}">Forgot your password?</a>
    </form>
</div>