<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Sign in</title>
    % endif
</%def>
<%def name="content()">
${c.form.start(h.url(controller=c.controller_name, action="password"), name="signin", method="post")}
    <fieldset>
        <legend>Send Password Reminder</legend>
        <p>
          <label for="username">Account Username:<br />
          ${c.form.text(name="username", class_="txt", id="username")}<br />
          ${c.form.get_error('username', format='<span class="bad">%s</span>')}</label>
        </p>
       <br />
    </fieldset>
    <input style="margin:1em" type="submit" value="Send Reminder"/>
</form>
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>
