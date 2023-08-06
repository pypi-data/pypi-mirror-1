<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if title is not UNDEFINED:
    <title>${title|n}</title>
    % else:
    <title>Index</title>
    % endif
</%def>
<%def name="content()">
        <h1>
        % if not(title is UNDEFINED):
                ${title|n}
        % else:
                ${"""%s's Account""" % c.auth_user.capitalize()|n }
        % endif
        </h1>
        % if not(msg is UNDEFINED):
                ${msg|n}
        % else:
        <p>${"""Welcome to the <em>&laquo;My Account&raquo;</em> area, %s. From here you can do the following:""" % c.auth_user.capitalize()|n}</p>
        % endif
        % for user in c.users:
        <p>${user.username} :: ${user.fullname} :: ${user.registered}</p>
        % endfor
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>
