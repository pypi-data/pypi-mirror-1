# -*- coding: utf-8 -*-
<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>Dashboard :: ${c.title or 'Index'|n}</title>
    % endif
    <link type="text/css" rel="stylesheet" href="/css/dashboard.css" media="screen" />
</%def>
<%def name="content()">
        <div class="editbox">
            <div class="edith1"><span class="warn">${c.title|n}</span> 
            <a href="/groups" title="${_('Group admin')}"
            >Group admin <img class="hicon" src="/img/silk/page_white_stack.png" alt=""/></a>  
            <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
            >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a></div>
% if c.w and c.w.form and c.action:
            <div id="twform">
    ${c.w.form.display(c.value, action=c.action)|n}
            </div>
% endif
        </div>
</%def>
<%def name="lhcolumn()">
    <%include file="adminnav.mak" />
    <%include file="motd.mak" />
</%def>
