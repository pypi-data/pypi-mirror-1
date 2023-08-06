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
<div class="edith1"><span class="warn">${_('Group Administration')}</span>  
     <a style="margin-left:2em" href="${url('new_group')}" title="${_('Add new group')}"
         >Add new group <img src="/img/silk/group_add.png" alt="" /></a>
    <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
        >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a>
</div>
<table class="editlist" id="groupeditlist" summary="Group list">
    <tr id="hdr">
        <td>${_('Group name')}</td>
        <td class="ctr">${_('Active y/n')}</td>
        <td class="ctr">${_('Edit group')}</td>
        <td class="ctr">${_('Delete group')}</td>
    </tr>
    <tr><td colspan="4"><hr /></td></tr>
    % for group in c.groups:
    <tr>
        <td><a class="thickbox" title="${group.name}"
            href="${h.url('groups_popup', id=group.id)}?height=400&amp;width=600">${group.name}</a></td>
        <td class="ctr"><img src="/img/assets/${'yes' if group.active else 'no'}.gif" alt="" /></td>
        <td class="ctr"><a href="${h.url('edit_group', id=group.id)}" 
               title="${_('Edit group')}"><img src="/img/silk/pencil.png" alt="" /></a></td>
        <td class="ctr"><a href="${h.url('delete_group', id=group.id)}"
                 title="${_('Delete group')}" onclick="confirmDelete('${group.name}',${group.id})"
                 ><img src="/img/silk/delete.png" alt="" /></a></td>
    </tr>
    % endfor
</table>
</%def>
<%def name="lhcolumn()">
    <%include file="adminnav.mak" />
    <%include file="motd.mak" />
</%def>
