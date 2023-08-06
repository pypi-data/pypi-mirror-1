<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>${c.title}</title>
    <style type="text/css">
    th {text-align: left; background-color: #eef; padding:0.25em 0;}
    </style>
</head>
<body>
    <h1>Identity model data requested by [<span style="font-style:italic;color:red">${c.auth_user.username}</span>]</h1>
    <h4>Users</h4>
    <table style="width:100%;padding:0 1em; font-size:75%">
        <tr>
            <th>username</th>
            <th>email</th>
            <th>password</th>
            <th>created</th>
            <th>active</th>
        </tr>
        % for u in c.users:
        <tr>
            <td>${u.username}</td>
            <td>${u.email}</td>
            <td>${u.password}</td>
            <td>${u.created}</td>
            <td>${u.active}</td>
        </tr>
        % endfor
    </table>

    <h4>Groups</h4>
    <table style="width:100%;padding:0 1em; font-size:75%">
        <tr>
##            <th>name</th>
            <th>description</th>
            <th>created</th>
            <th>active</th>
##            <th>users</th>
##            <th>permissions</th>
        </tr>
        % for g in c.groups:
        <tr>
##            <td>${g.name}</td>
            <td>${g.description}</td>
            <td>${g.created}</td><td>${g.active}</td>
##            <td>${', '.join([u.username for u in g.users])}</td>
##            <td>${', '.join([p.name for p in g.permissions])}</td>
        </tr>
    % endfor
    </table>

    <h4>Permissions</h4>
    <table style="width:100%;padding:0 1em; font-size:75%">
        <tr>
            <th>name</th>
            <th>description</th>
##            <th>groups</th>
        </tr>
        % for p in c.permissions:
        <tr><td>${p.name}</td><td>${p.description}</td>
##        <td>${', '.join([group.name for group in p.groups])}</td>
        </tr>
    % endfor
    </table>
</body>
</html>
