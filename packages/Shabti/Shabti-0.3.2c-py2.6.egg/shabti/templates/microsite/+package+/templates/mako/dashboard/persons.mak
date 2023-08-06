# -*- coding: utf-8 -*-
<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>Dashboard :: ${c.title or 'Index'}</title>
    % endif
    <link type="text/css" rel="stylesheet" href="/css/dashboard.css" media="screen" />
    <link type="text/css" rel="stylesheet" href="/css/cmxform.css" media="screen" />
    <script type="text/javascript" src="/js/thickbox.js">
</script>
    <link type="text/css" rel="stylesheet" href="/css/thickbox.css" media="screen" />
</%def>
<%def name="content()">
<div class="edith1"><span class="warn">${_('Users Administration')}</span>  
     <a style="margin-left:2em" href="${h.url('new_user')}" title="${_('Add new user')}"
         >Add new user <img src="/img/silk/user_add.png" alt="" /></a>
    <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
        >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a>
</div>
<table class="editlist" id="usereditlist"summary="Persons list">
    <tr id="hdr">
        <td>${_('User name')}</td>
        <td>Created:</td>
        <td class="ctr">Active?</td>
        <td class="ctr">${_('Edit details')}</td>
        <td class="ctr">${_('Delete account')}</td>
    </tr>
    <tr><td colspan="6"><hr /></td></tr>
    % for user in c.users:
    <tr>
        <td><a class="thickbox" title="${user.username}"
            href="${h.url('users_popup', id=user.id)}?height=400&amp;width=600">${user.username}</a></td>
        <td>${user.created}</td>
        <td class="ctr"><img src="/img/assets/${'yes' if user.active else 'no'}.gif"alt=""/></td>
        <td class="ctr"><a href="${h.url('edit_user', id=user.id)}" 
               title="${_('Edit')}"><img src="/img/silk/pencil.png" alt=""/></a></td>
        <td class="ctr">
        % if user.id != c.userid:
            <a href="${h.url('delete_user', id=user.id)}" title="${_('Delete user')}"
                onclick="confirmDelete('${user.username}',${user.id})"
                ><img src="/img/silk/pencil_delete.png" alt="" /></a>
        % else:
            <img src="/img/silk/pencil_delete.png" alt="" />
        % endif
        </td>
    </tr>
    % endfor
</table>
</%def>
<%def name="lhcolumn()">
    <%include file="adminnav.mak" />
    <%include file="motd.mak" />
</%def>
