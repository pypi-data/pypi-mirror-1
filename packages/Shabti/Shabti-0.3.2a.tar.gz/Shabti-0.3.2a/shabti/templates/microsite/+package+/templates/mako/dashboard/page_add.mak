# -*- coding: utf-8 -*-
<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    <link type="text/css" rel="stylesheet" href="/css/dashboard.css" media="screen" />
    <link type="text/css" rel="stylesheet" href="/css/cmxform.css" media="screen" />
    % if c.title is not UNDEFINED:
    <title>Dashboard :: ${c.title or 'Index'}</title>
    % endif
</%def>
<%def name="content()">
    <div class="editbox">
        <div class="edith1"><span class="warn">${_('Add page')}</span>
            <a href="/pages" title="${_('Pages')}"
            >Page admin <img class="hicon" src="/img/silk/page_white_stack.png" alt=""/></a>  
            <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
            >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a>
        </div>
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
