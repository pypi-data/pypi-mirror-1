<%inherit file="headerfooter.mako" />

<ul>
    
    <li>
        <a href="${h.url_for(controller='prebeliever', action='list')}">Prebelievers</a>:
        <a href="${h.url_for(controller='prebeliever', action='add')}">Add</a>
    </li>
    
    <li>
        <a href="${h.url_for(controller='submitter', action='list')}">Submitters</a>:
        <a href="${h.url_for(controller='submitter', action='add')}">Add</a>
    </li>
    
    <li>
        <a href="${h.url_for(controller='administrator', action='list')}">Administrators</a>:
        <a href="${h.url_for(controller='administrator', action='add')}">Add</a>
    </li>
    
    <li>
        <a href="${h.url_for(controller='believer', action='list')}">Believers</a>
    </li>
    
</ul>

    <hr />
    
<ul>
    <li><a href="${h.url_for(controller='administrator', action='edit_email')}">Change My Email Address</a></li>
    <li><a href="${h.url_for(controller='administrator', action='edit_password')}">Change My Password</a></li>
</ul>