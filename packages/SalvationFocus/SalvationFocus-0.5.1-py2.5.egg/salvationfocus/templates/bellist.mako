<%inherit file="list.mako" />

% for bel in c.list:
    <tr>
        <td>${bel.first_name.capitalize()} ${bel.last_name.capitalize()}</td>
        <td>${bel.date_entered}</td>
        
        % if bel.last_viewed:
            <td>${bel.last_viewed}</td>
        % else:
            <td>Never</td>
        % endif
        
        % if bel.times_viewed:
            <td>${bel.times_viewed}</td>
        % else:
            <td>0</td>
        % endif
        
        <td>${bel.date_answered}</td>
    </tr>
% endfor