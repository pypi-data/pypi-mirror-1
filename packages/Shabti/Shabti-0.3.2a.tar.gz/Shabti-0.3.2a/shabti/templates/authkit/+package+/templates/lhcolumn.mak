<%! import datetime, os %>
<div id="navarea" style="font-size:90%; margin-left: 1.5em">
    % if c.auth_user:
        <ul>
            <li>
                ${h.link_to('Change your password', 
                             h.url(controller=c.controller_name, action='change_password'))|n}
            </li>
            <li>
                ${h.link_to('Register a new email address', 
                            h.url(controller=c.controller_name, action='register_new_email'))|n}
            </li>
            <li>
                ${h.link_to('Update your details', 
                            h.url(controller=c.controller_name, action='update_details'))|n}
            </li>
            <li>
                ${h.link_to('Sign Out', 
                                h.url(controller=c.controller_name, action='signout'))|n}
            </li>
        </ul>
    % else:
    <form action="/account/signin" method="post" name="manual_signin"> 
    <fieldset> 
        <legend>Sign in</legend> 
        <p style="margin-left:1em"> 
          <label for="username">Username:<br /> 
          <input class="txt" id="username" name="username" type="text" /> 
          <br /> 
          
          </label> 
        </p> 
        <p style="margin-left:1em"> 
          <label for="password">Password:<br /> 
          <input class="txt" id="password" name="password" type="password" value="" /> 
          <br /> 
          
          </label> 
        </p> 
        <input style="margin-left:1em" type="submit" value="Sign In" class="submit" /> 
        <input type="hidden" value="1" name="signin_attempt" class="submit" /> 
     % endif
        <div style="font-size:80%;margin:1em 0 0 1em;">${datetime.datetime.utcnow().strftime("%c")} GMT</div>
    </fieldset>
    </form>
    <ul>
        <li>
            ${h.link_to("Sign up for an account", 
                            h.url(controller=c.controller_name, action='register'))}
        </li>
    </ul>
</div>


