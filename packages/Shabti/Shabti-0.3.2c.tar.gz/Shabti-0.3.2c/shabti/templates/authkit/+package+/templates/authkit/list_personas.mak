<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Personas</title>
    % endif
</%def>
<%def name="content()">
${c.msg}
% if c.personas:
    <p>Available personas:</p>
    <table border="0">
% for persona in c.personas:
        <tr>
            <td>${persona.name}</td>\
% if persona.name == c.persona_selected:
            <td>default</td>\
% else:
            <td></td>\
% endif
            <td>[${h.link_to("update", h.url(controller=c.controller_name, action="personas", id=persona.uid))}]</td>
        </tr>
% endfor
    </table>
% else:
<p>No personas have been setup</p>
% endif

<p>${h.link_to("Add a new persona", h.url(controller=c.controller_name, action="personas", id="new") )}</p>
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>

