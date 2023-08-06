<%inherit file="headerfooter.mako" />

<table>
    ##Title
    <caption>${c.title.capitalize()}s</caption>
    
    ##Headers
    <tr>
    % for header in c.headers:
        <th>${header}</th>
    % endfor
    </tr>
    
    ##Data
    ${next.body()}
    
</table>

% if c.begin > 1:
    <a href="${h.url_for(controller=c.title, action='list', begin=c.begin - 20 if c.begin > 19 else 0)}">&lt;&lt; Previous</a>
% endif
Showing ${c.begin + 1} - ${c.end} of ${c.total} ${c.title.lower()}s.
% if c.end < c.total:
    <a href="${h.url_for(controller=c.title, action='list', begin=c.end)}">Next &gt;&gt;</a>
% endif