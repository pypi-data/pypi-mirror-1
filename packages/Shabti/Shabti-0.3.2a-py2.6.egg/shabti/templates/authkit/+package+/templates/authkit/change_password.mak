<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Change password</title>
    % endif
</%def>
<%def name="content()">

${c.form.start(h.url(controller=c.controller_name, action='change_password'), name="signin", method="post")}
<fieldset>
    <legend>Change Password</legend>

% if not c.ignore_old_password is UNDEFINED:
    <p>
      <label for="email">Current Password:<br />
      ${c.form.password(name="password", class_="txt", id="email")}
      ${c.form.get_error('password', format='<span class="bad">%s</span>')}</label>
    </p>
    
% else:
	${c.form.hidden(name="password")}
	${c.form.hidden(name="ignore_old_password", value=1)}
% endif

    <p>
      <label for="password">Password:<br />
      ${c.form.password(name="newpassword", value='', class_="txt", id="newpassword")}
      ${c.form.get_error('newpassword', format='<span class="bad">%s</span>')}</label>
    </p>
    <p>
      <label for="password">Password Confirm:<br />
      ${c.form.password(name="cnewpassword", value='', class_="txt", id="cnewpassword")}
      ${c.form.get_error('cnewpassword', format='<span class="bad">%s</span>')}</label>
    </p>
    <input style="margin:1em" type="submit" value="Submit" class="submit" />
<br />
</fieldset>
${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>
