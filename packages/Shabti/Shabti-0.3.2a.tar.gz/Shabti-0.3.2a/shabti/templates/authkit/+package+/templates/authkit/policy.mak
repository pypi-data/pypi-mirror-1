<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Privacy Policy</title>
    % endif
</%def>
<%def name="content()">
<p>This page should describe the privacy policy of the site.</p>

<p>If you use the passurl registration facility the identity provider 
will show the user this URL when they are choosing which registration 
information should be sent back to this software so this page should 
let the user know what you will do with the information they enter.</p>
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>
