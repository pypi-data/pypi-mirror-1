<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Change Email</title>
    % endif
</%def>
<%def name="content()">
<p>Your contact email is the address where we'll send you notifications. Your contact email must always be a valid address.</p>

${c.form.start(h.url(controller=c.controller_name, action="register_new_email"), name="signin", method="post")}
<fieldset>
    <legend>Emails</legend>
    <p>
      <label for="surname">New Email:<br />
      ${c.form.text(name="email", class_="txt", id="email")}<br />
      ${c.form.get_error('email', format='<span class="bad">%s</span>')}</label>
    </p>
</fieldset>
<p><input style="margin:1em" type="submit" value="Save" class="submit" /></p>
${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>

