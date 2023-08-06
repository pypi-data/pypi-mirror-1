<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Sign up</title>
    % endif
    <!-- Script -->
    % if 'username' in c.show:
        ${h.javascript_include_tag('/script/signup.js')|n}
    % endif
</%def>
<%def name="content()">
    <h1>User Registration Form</h1>

    % if c.use_passurl:
        ${c.form.start(h.url(controller=c.controller_name, action="passurl"), name="passurl_signup", id="passurl_signup", method="post")}
        <fieldset>
            <legend>Automatic Registration</legend>
            <p>
              <label for="passurl">Passurl or OpenID: <small>(<a href="http://passurl.com">What's this about?</a>)</small><br />
              ${c.form.text(name="passurl", class_="txt", id="passurl")} 
              <input type="submit" class="submit" value="Register" />
              <br />
              ${c.form.get_error('passurl', format="""<span class="bad">%s</span>""")}
              </label>
            </p>
            ${c.form.hidden(name="mode", value="register")}
        </fieldset>
        </form>

        % if not c.mode == "passurl":
            <p>or</p>
        % endif 
    % endif

% if not c.mode == "passurl":

    ${c.form.start(h.url(controller=c.controller_name, action=c.action or "register_manual"), name="manual_signup", id="signup", method="post")}
                                    
    <fieldset>
        <legend>\
        % if c.action != 'register_automatic':
            Manual Registration\
        % else:
            Automatic Registration\
        % endif
        </legend>
        <p>
            <label for="username">Username\
    % if c.show_required:
*\
    % endif \
:<br />
                ${c.form.text(
        name="username", 
        class_="txt", 
        maxlength=20, 
        id="username", 
        onkeyup="copy_username();",
        onblur="check_username_availability(); return false;")} <small>(this could be your nickname)</small>
                <br /><span id="loader" class="loader">${c.form.get_error('username', format="""<span class="bad">%s</span>""")}</span>
            </label>
        </p>
        <p>Your URL will look like this: <strong><span class="highlight" id="usernamecheck">&lt;username&gt;</span>.example.com</strong></p>
    % if c.fields['required'] and c.show_required:
        <p>Fields marked * must be completed.</p>
    % endif
    % for field in c.sreg_fields:
        % if field not in c.show and c.action == 'register_automatic':
            ${c.form.hidden(name=field)}
        % endif
        % if field in c.show:
            % if field in c.fields['required'] or field in c.fields['optional']:
                <p>
                % if field in ['dob']:
                    <label for="${field}">Date of Birth\
                % else:
                    <label for="${field}">${field.capitalize()}\
                % endif
                % if field in c.fields['required'] and c.show_required:
* 
                % endif
:<br />
                % if field in ['dob']:
                    ${c.form.dropdown(name=field+".day", values=None, class_="txt", id=field+"_day", options=c.days)}
                    ${c.form.dropdown(name=field+".month", values=None, class_="txt", id=field+"_month", options=c.months)}
                    ${c.form.dropdown(name=field+".year", values=None, class_="txt", id=field+"_year", options=c.years)}
                % elif field in ['country','timezone','language','gender','username']:
                    ${c.form.dropdown(name=field, values=None, class_="txt", id=field, options=getattr(c, field))}
                % else:      
                    ${c.form.text(name=field, class_="txt", id=field)}
                % endif
                <br />${c.form.get_error(field, format="""<span class="bad">%s</span>""")}</label>
                </p>
            % endif
        % endif
    % endfor
    % if 'password' in c.show:
        <p>
          <label for="password">Password\
        % if c.show_required:
*\
        % endif \
:<br />
        ${c.form.password(name="password", class_="txt", id="password")}
        <br />${c.form.get_error('password', format="""<span class="bad">%s</span>""")}</label>
        </p>
        <p>
            <label for="cpassword">Confirm Password\
        % if c.show_required: 
*\
        % endif \
:<br />
        ${c.form.password(name="cpassword", class_="txt", id="cpassword", onblur="check_password();")}
            <br /><span id="checkpassword">${c.form.get_error('cpassword', format="""<span class="bad">%s</span>""")}</span></label>
        </p>
    % endif
        <div id="terms" style="display: None; padding: 0px; margin:0px;">
            <p>Terms and Conditions: <span onclick="fade('terms')"><a href="#"><small>(hide)</small></a></span><br />
                <textarea cols="80" rows="10">You accept that this site is in development and most likely does not work. You agree not to use it for any purpose and do not hold the author responsible for any problems that arise should ignore these terms.</textarea>
        </div>

        <p>${c.form.checkbox(name="agree")} I agree to the <span onclick="appear('terms'); return false;"><a href="#">Terms and Conditions</a></span></p>

        ${c.form.get_error('agree', format="""<span class="bad">%s</span>""")}

        <input style="margin:1em;" type="submit" class="submit" value="Register" />
    </fieldset>
    </form>
% endif
</%def>
<%def name="lhcolumn()">
    <%include file="/lhcolumnunsigned.mak" />
</%def>
