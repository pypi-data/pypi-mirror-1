# -*- coding: utf-8 -*-
## Based on standard 3-col Show-both derivation
## Defines "content", "lhcolumn" and "rhcolumn" fragments

<%inherit file="/core/show-both.mak"/>
<%def name="header()">
    <link type="text/css" rel="stylesheet" href="/css/sphinx.css" media="screen" />
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>{{package}} :: Default</title>
    % endif
</%def>
<%def name="content()">
                                <h1>${c.title}</h1>
                                ## DEBUG <pre style="font-size: 70%;">${c.reqenv}</pre>
                                <p>Public Access Page</p>

</%def>
<%def name="rhcolumn()">
    %if c.auth_user:
<div id="accessibility">
    <h3>Your Account</h3>
    <h5>${c.auth_user if c.auth_user else 'Not signed in'}</h5>
    <ul>
        <li><a href="/account/signin">Sign in</a></li>
        <li><a href="/account/signout">Sign out</a></li>
        % for k in (('Change your password','change_password'),('Register a new email address','register_new_email'), ('Update your details','update_details')):
        <li>${h.link_to(k[0], h.url(controller="account", action=k[1]))}</li>
        % endfor
    </ul>
</div>
    % else:
<div id="accessibility">
    <h3>Guest (no account)</h3>
    <ul>
        <li><a href="/account/register">Register for an account</a></li>
    </ul>
</div>
    % endif
</%def>

<%def name="lhcolumn()">
    <%include file="lhcolumn.mak" />
</%def>
