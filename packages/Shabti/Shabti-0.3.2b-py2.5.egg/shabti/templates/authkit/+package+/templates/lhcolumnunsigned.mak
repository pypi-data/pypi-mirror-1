<div id="navarea">
    <h3>Other Options</h3>
    <div style="font-size:90%; margin-left: 1.5em">
        <ul>
            <li>${h.link_to("Sign up for an account", h.url(controller=c.controller_name, action='register'))}</li>
            <li>${h.link_to("Request a password reminder", h.url(controller=c.controller_name, action='password'))}</li>
            <li>${h.link_to("Enter an email verification code", h.url(controller=c.controller_name, action='confirm'))}</li>
            <li>${h.link_to("Request a new verification code", h.url(controller=c.controller_name, action='code'))}</li>
        </ul>
    </div>
</div>
