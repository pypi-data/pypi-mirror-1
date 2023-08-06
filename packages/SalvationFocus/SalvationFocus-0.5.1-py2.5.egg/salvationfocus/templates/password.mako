<%inherit file="base.mako" />

<form action="${h.url_for(controller='login', action='get_password')}" method="post">
    <label for="login_name">Login:</label><input type="text" title="Enter your login" name="login_name" id="login_name" value="" /><br />
    <input type="submit" value="Email my password" />
</form>