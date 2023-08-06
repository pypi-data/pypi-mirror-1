<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Verify Email Address</title>
    % endif
</%def>
<%def name="content()">
${c.form.start(h.url(controller=c.controller_name, action="confirm"), name="signin", method="post")}
<fieldset>
    <legend>Enter a Code</legend>

    <p>
      <label for="username">Username:<br />
      ${c.form.text(name="username",  class_="txt", id="verificationusername")}
      <br />${c.form.get_error('username', format='<span class="bad">%s</span>')}</label>
    </p>

    <p>
      <label for="code">Verification code:<br />
      ${c.form.text(name="code", value='', class_="txt", id="verificationcode")}
      <br />${c.form.get_error('code', format='<span class="bad">%s</span>')}</label>
    </p>
    <input style="margin:1em" type="submit" value="Verfiy" class="submit" />
</fieldset>
${c.form.end()}
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumnunsigned.mak" />
</%def>

