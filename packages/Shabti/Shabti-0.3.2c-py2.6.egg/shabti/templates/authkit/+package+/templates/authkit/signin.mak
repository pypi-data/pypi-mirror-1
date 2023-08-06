<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Sign in</title>
    % endif
</%def>
<%def name="content()">
                                <h1>Sign in</h1>

% if c.use_passurl:
${c.form.start(h.url(controller=c.controller_name, action="passurl"), name="passurl_signin", method="post")}
<fieldset>
    <legend>Using your Passurl</legend>
    <p>
      <label for="passurl">Passurl or OpenID: <small>(<a href="http://passurl.com">What's this about?</a>)</small><br />
      ${c.form.text(name="passurl", class_="txt", id="passurl")}
      <input type="submit" class="submit" value="Sign In" />
      
      <br />
      ${c.form.get_error('passurl', format='<span class="bad">%s</span>')|n}
      </label>
    </p>
    ${c.form.hidden(name="mode", value="signin")}
    ${c.form.hidden(name="signin_attempt",  value="1")}
    ${c.form.hidden(name="redirect_to")}

</fieldset>
</form>
    % if c.mode != 'passurl':
        <p>or</p>
    % endif
% endif

% if c.mode != 'passurl':
    ${c.form.start(h.url(controller=c.controller_name, action="signin"), name="manual_signin", method="post")}
    <fieldset>
        <legend>Manually</legend>
        <p>
          <label for="username">Username:<br />
          ${c.form.text(name="username", class_="txt", id="username")}
          <br />
          ${c.form.get_error('username', format='<span class="bad">%s</span>')|n}
          </label>
        </p>
        <p>
          <label for="password">Password:<br />
          ${c.form.password(name="password", value='', class_="txt", id="password")}
          <br />
          ${c.form.get_error('password', format='<span class="bad">%s</span>')|n}
          </label>
        </p>
     <input style="margin: 1em" type="submit" value="Sign In" class="submit" />
     <input type="hidden" value="1" name="signin_attempt" class="submit" />
    
        ${c.form.hidden(name="redirect_to")}
        <br />

    </fieldset>
    ${c.form.end()}


% endif
</%def>
<%def name="lhcolumn()">
<div id="navarea">
    <h3>Other Options</h3>
    <p style="margin-left:0.1em;font-size:90%">&raquo; 
    ${h.link_to("Sign up for an account", h.url(controller=c.controller_name, action='register'))}
    <br />
    &raquo; 
    ${h.link_to("Request a password reminder", h.url(controller=c.controller_name, action='password'))} 
    <br />
    &raquo; 
    ${h.link_to("Enter an email verification code", h.url(controller=c.controller_name, action='confirm'))} 
    <br />
    &raquo; 
    ${h.link_to("Request a new verification code", h.url(controller=c.controller_name, action='code'))}
</div>
</%def>
