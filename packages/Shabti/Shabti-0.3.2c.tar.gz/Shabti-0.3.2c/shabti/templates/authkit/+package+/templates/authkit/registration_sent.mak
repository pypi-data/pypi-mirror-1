<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Confirmation Email Sent</title>
    % endif
</%def>
<%def name="content()">
% if c.register:
<p>We've just sent you a verification email to ${c.email|n}. \
% endif
% if c.new_email:
<p>A new verification code has just been sent to ${c.email|n}.\
% endif
It should reach you in a few seconds but may take slightly longer depending on your email provider.</p>


<p>Please click on the link contained in the email or enter your verification code below to verify your email address:</p>

${c.form.start(h.url(controller=c.controller_name, action="confirm"), name="signin", method="post")}
<fieldset>
    <legend>Enter a Code</legend>

    <input type="hidden" name="username" value="${c.username}" />

    <p>
      <label for="code">Verification code:<br />

      ${c.form.text(name="code", value='', class_="txt", id="verification")}
      <br />${c.form.get_error('code', format='<span class="bad">%s</span>')}</label>
    </p>
    <input style="margin:1em" style="margin:1em;" type="submit" value="Verfiy" class="submit" />
</fieldset>
${c.form.end()}


<p>If you don't see the verification email in your inbox try checking your spam/junk mail folder it may have been filtered from your inbox by mistake. To prevent this happening in future please put us on your safe list. If you email address is not ${c.email} or no verification code is received you should ${h.link_to('request a new verification code', h.url(controller=c.controller_name, action='code'))}.</p>
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumn.mak" />
</%def>

