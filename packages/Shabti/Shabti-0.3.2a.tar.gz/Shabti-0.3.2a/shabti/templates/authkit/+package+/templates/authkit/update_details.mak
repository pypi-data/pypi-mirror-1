<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Update Details</title>
    % endif
</%def>
<%def name="content()">
${c.form.start(h.url(controller=c.controller_name, action="update_details"),name="signin", method="post")}
<fieldset>
    <legend>Details</legend>
    <p>
      <label for="firstname">Firstname:<br />
      ${c.form.text(name="firstname", class_="txt", id="firstname")}<br />
      ${c.form.get_error('firstname', format='<span class="bad">%s</span>')}</label>
    </p>
    <p>
      <label for="surname">Surname:<br />
      ${c.form.text(name="surname", class_="txt", id="surname")}<br />
      ${c.form.get_error('surname', format='<span class="bad">%s</span>')}</label>
    </p>
    <p>
      <label for="email">Email Address:<br />
      ${c.form.dropdown(name="email", values=c.emails, class_="txt", id="email", options=c.emails)} ${h.link_to("Register new email", h.url(controller=c.controller_name, action="register_new_email"))}<br />
      ${c.form.get_error('email', format='<span class="bad">%s</span>')}</label>
    </p>
    <p>
      <label for="session">Session Length<br />
      ${c.form.text(name="session", class_="txt", id="session")}<br />
      ${c.form.get_error('session', format='<span class="bad">%s</span>')}</label>
    </p>

</fieldset>
<p>
<input style="margin:1em" type="submit" value="Save" class="submit" />
</p>

${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>


