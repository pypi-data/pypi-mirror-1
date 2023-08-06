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
<div class="edith1"><span class="warn">${_('Page Administration')}</span>  
     <a style="margin-left:2em" href="${url('new_page')}" title="${_('Add new page')}"
         >Add new page <img src="/img/silk/page_add.png" alt="" /></a>
    <a style="margin-left:2em" href="/dashboard/index" title="${_('Dashboard')}"
        >Dashboard <img class="hicon" src="/img/silk/folder_wrench.png" alt=""/></a>
</div>
<table class="editlist" id="pageeditlist" summary="Pages list">
    <tr id="hdr">
        <td>${_('Page title')}</td>
        <td class="ctr">${_('Display y/n')}</td>
        <td class="ctr">${_('Edit page')}</td>
        <td class="ctr">${_('Delete page')}</td>
    </tr>
    <tr><td colspan="4"><hr /></td></tr>
    % for page in c.pages:
    <tr>
        <td><a class="thickbox" title="${page.title}"
            href="${h.url('pages_popup', id=page.id)}?height=400&amp;width=600" >${page.title}</a></td>
        <td class="ctr"><img src="/img/assets/${'yes' if page.display else 'no'}.gif" alt="" /></td>
        <td class="ctr"><a href="${h.url('edit_page', id=page.id)}" 
               title="${_('Edit page')}"><img src="/img/silk/pencil.png" alt="" /></a></td>
        <td class="ctr"><a href="${url('delete_page', id=page.id)}" 
               title="${_('Delete page')}" onclick="confirmDelete('${page.slug}', ${page.id});"
               ><img src="/img/silk/delete.png" alt="" /></a>
        </td>
    </tr>
    % endfor
</table>
</%def>
<%def name="lhcolumn()">
    <%include file="adminnav.mak" />
</%def>



