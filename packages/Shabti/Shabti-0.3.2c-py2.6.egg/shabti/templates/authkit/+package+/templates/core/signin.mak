# -*- coding: utf-8 -*-
<%def name="body()">
% if c.user is not UNDEFINED and c.user > 1:
    <div id="pageLogin">«<a href="/account/" class="no-border">My Account</a>» / «<a href="/account/signout/" class="no-border">Sign Out</a>»</div>
% else:
    <div id="pageLogin">«<a href="/account/signin/" class="no-border">Sign In</a>» / «<a href="/account/register/" class="no-border">Register</a>»</div>
% endif
</%def>
