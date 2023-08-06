<%inherit file="list.mako" />

% for pre in c.list:
    <tr>
        <td>${pre.first_name.capitalize()} ${pre.last_name.capitalize()}</td>
        <td>${pre.date_entered}</td>
        
        % if pre.last_viewed:
            <td>${pre.last_viewed}</td>
        % else:
            <td>Never</td>
        % endif
        
        % if pre.times_viewed:
            <td>${pre.times_viewed}</td>
        % else:
            <td>0</td>
        % endif
        
        <td>${pre.submitter.first_name.capitalize()} ${pre.submitter.last_name.capitalize()}</td>
	<td><a href="${h.url_for(controller='prebeliever', action='edit', id=pre.id)}" >Edit</a></td>
	<td><a href="${h.url_for(controller='prebeliever', action='saved', id=pre.id)}" >Believer</a></td>
    </tr>
% endfor