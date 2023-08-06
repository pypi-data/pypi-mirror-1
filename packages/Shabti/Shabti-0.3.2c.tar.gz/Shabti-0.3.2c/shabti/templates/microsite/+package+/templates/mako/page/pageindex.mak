# -*- coding: utf-8 -*-
## Based on standard 2-col Hide-Right derivation
## Defines "content" and "lhcolumn" fragments

<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title|n}</title>
    % else:
    <title>Bel-EPA :: Pages</title>
    % endif
</%def>
<%def name="content()">
        <h1>Pages</h1>
        <p>List of pages</p>
        % for page in c.pages:
            <h3><a href="${h.url(controller='/page',action='view',id=page.slug)}">${page.title|n}</a></h3>
            <p>${h.markdown.markdown(page.content)|n}</p>
        % endfor
</%def>
<%def name="lhcolumn()">
    <%include file="../lhcolumn.mak" />
</%def>
