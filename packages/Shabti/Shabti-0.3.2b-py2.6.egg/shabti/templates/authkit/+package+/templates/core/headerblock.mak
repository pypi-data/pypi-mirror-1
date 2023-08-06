# -*- coding: utf-8 -*-
<%def name="body()">
    <div id="headerblock">
        <h2 class="displaynone">${('Site navigation')}</h2>
        <a id="navareatag">
        </a>
        <ul>
            <li id="home"><a href="/hello/index" accesskey="1" title="Home Page shortcut key = alt + 1">home</a></li>
            <li id="about"><a href="/auth/private" title="The about page">authtest</a></li>
            <li id="account"><a href="/account/index" title="Account management">accounts</a></li>
        </ul>
        % if c.flash:
            <div id="statusmessage" class="flash">${c.flash}</div>
        % endif
    </div>
</%def>
