<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Request New Verification Code</title>
    % endif
</%def>
<%def name="content()">
<p>Please complete the form below to send a new verification code. Any old 
   codes will no longer be valid after the new code is sent.
</p>

${c.form.start(h.url(controller=c.controller_name, action="code"), name="signin", method="post")}
<fieldset>
<legend>Request a new Code</legend>
    <p>
      <label for="username">Username:<br />
      ${c.form.text(name="username", class_="txt", id="username" )}
      <br />${c.form.get_error('username', format='<span class="bad">%s</span>')}
      </label>
    </p>
    <p>
      <label for="password">Password:<br />
      ${c.form.password(name="password", class_="txt", id="password")}
      <br />${c.form.get_error('password', format='<span class="bad">%s</span>')}</label>
    </p>
    <p>
      <label for="surname">Email Address:<br />
      ${c.form.text(name="email", class_="txt", id="email")}
      <br />${c.form.get_error('email', format='<span class="bad">%s</span>')}</label>
    </p>
<input style="margin:1em" type="submit" value="Request Code" class="submit" />

</fieldset>
${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumnunsigned.mak" />
</%def>
