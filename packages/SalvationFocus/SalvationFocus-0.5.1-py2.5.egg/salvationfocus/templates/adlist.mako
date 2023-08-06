<%inherit file="list.mako" />

% for ad in c.list:
    <tr>
        <td>${ad.login_name}</td>
        <td>${ad.email}</td>
    </tr>
% endfor