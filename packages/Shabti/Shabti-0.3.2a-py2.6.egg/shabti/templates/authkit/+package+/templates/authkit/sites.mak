<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Approved Sites</title>
    % endif
</%def>
<%def name="content()">
${c.msg}

% if c.approved_trust_roots:
    <p>Approved trust roots:</p>
    <ul>
% for site in c.approved_trust_roots:
        <li><tt>${site.trustroot}</tt> [<a href="${h.url(controller=c.controller_name, action='sites', id=site.uid)}">remove</a>]</li>
% endfor
    </ul>
% else:
    <p>No approved sites</p>
% endif
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>

