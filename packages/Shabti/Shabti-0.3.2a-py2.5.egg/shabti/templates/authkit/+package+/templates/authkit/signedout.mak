<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Signed Out</title>
    % endif
</%def>
<%def name="content()">
<p>You have been signed out. ${h.link_to("Sign in again", h.url(controller=c.controller_name, action='signin'))}.</p></%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumnunsigned.mak" />
</%def>


