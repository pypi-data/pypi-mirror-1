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
<div class="edith1"><span class="warn">${_('Permissions Administration')}</span>  
     <a style="margin-left:2em" href="${url('new_permission')}" title="${_('Add new permission')}"
         >Add new permission <img src="/img/silk/permission_add.png" alt="" /></a>
    <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
        >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a>
</div>
<table class="editlist" id="permissioneditlist" summary="Permissions list">
    <tr id="hdr">
        <td>${_('Permission name')}</td>
        <td class="ctr">${_('Edit permission')}</td>
        <td class="ctr">${_('Delete permission')}</td>
    </tr>
    <tr><td colspan="4"><hr /></td></tr>
    % for permission in c.permissions:
    <tr>
        <td><a class="thickbox" title="${permission.name}"
            href="${h.url('permissions_popup', id=permission.id)}?height=400&amp;width=600" 
            >${permission.name}</a></td>
        <td class="ctr"><a href="${h.url('edit_permission', id=permission.id)}" 
               title="${_('Edit permission')}"><img src="/img/silk/pencil.png" alt="" /></a></td>
        <td class="ctr"><a href="${h.url('delete_permission', id=permission.id)}"
               title="${_('Delete permission')}" 
               onclick="confirmDelete('${permission.name}',${permission.id});"
               ><img src="/img/silk/delete.png" alt=""/></a>
        </td>
    </tr>
    % endfor
</table>
</%def>
<%def name="lhcolumn()">
    <%include file="adminnav.mak" />
    <%include file="motd.mak" />
</%def>
