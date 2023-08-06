<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Persona</title>
    % endif
    % if c.new_persona:
    Add Persona
    % else:
    Update Persona
    % endif
</%def>
<%def name="content()">
${c.msg}

${c.form.start(name="signin", action=h.url(controller=c.controller_name, action="personas", id=c.id), method="post")}
<fieldset>
    <legend>Details</legend>

% if c.new_persona:
    <p>
      <label for="name">Persona Name:<br />
      ${c.form.text(name="name", class_="txt", id="name")}<br />
      ${c.form.get_error('name', format='<span class="bad">%s</span>')}</label>
    </p>
% endif

## <& /openid/server/persona.mak &>

</fieldset>
<p>
<input name="return_to" value="${request.params.get("return_to", '')}" type="hidden" />
<input style="margin:1em" name="go" value="Save" type="submit" />
</p>

${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>

