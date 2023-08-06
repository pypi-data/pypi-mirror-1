<%inherit file="list.mako" />

% for sub in c.list:
    <tr>
        <td>${sub.first_name.capitalize()} ${sub.last_name.capitalize()}</td>
        <td>${sub.phone}</td>
        <td>${sub.email}</td>
	<td><a href="${h.url_for(controller='submitter', action='edit', id=sub.id)}" >Edit</a></td>
    </tr>
% endfor