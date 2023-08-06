# -*- coding: utf-8 -*-
<%def name="body()">

    <div id="footer" class="clear" style="font-size:80%;">
        <ul>
            <li><a href="/" accesskey="1" title="Home Page shortcut key = alt + 1">Home</a></li>
            <li><a href="/page/about" accesskey="9" title="Contact us Feedback Form shortcut key = alt + 9">Contact</a></li>
            <li><a href="/page/sitemap" accesskey="3" title="Site Map shortcut key = alt + 3">Site map</a></li>
            % if c.user:
                <li>[ ${c.legend}:</li>
                <li><a href="/dashboard/index">${_('Dashboard')}</a></li>
                % if c.edit_url is not UNDEFINED:
                    <li><a href="${c.edit_url or '#'}">${_('Edit')}</a></li>
                % else:
                    <li>${_('Edit')}</li>
                % endif
                <li><a href="/login/signout">${_('Sign out')}</a> ]</li>
            % else:
                <li><a href="/login/index">${_('Admin')}</a></li>
            % endif
            <li><span style="color:black;">${c.dcmeta.copyright} 1995, ${c.dcmeta.copyrightyear}</span></li>
            <li><span style="font-style:italic">&#171; Pylons ${g.version} &#187; </span></li>
        </ul>
    </div>
    <form id="junk" action="#" method="get">
        <fieldset style="border:none;width:80%">
            <input type="hidden" id="flashTransport" name="flashTransport" value='${c.flash}' />
        </fieldset>
    </form>
</%def>

