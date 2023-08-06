<%inherit file="/core/hide-both.mak"/>
<%def name="header()">
    <title>Already signed out</title>
</%def>
<%def name="content()">
<p>You are already signed out. 
    ${h.link_to("Sign in again", h.url(controller=c.controller_name, action='signin'))}.</p>
</%def>
