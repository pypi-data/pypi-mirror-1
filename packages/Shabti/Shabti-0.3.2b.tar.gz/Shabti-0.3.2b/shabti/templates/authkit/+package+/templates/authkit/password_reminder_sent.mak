<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Password Reminder Sent</title>
    % endif
</%def>
<%def name="content()">
<p>A password reminder has been sent to the email address you registered your account with.</p>

<p>Please check your email and then <% h.link_to( 'sign in', h.url(controller=c.controller_name)) %>. </p>
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumnunsigned.mak" />
</%def>
