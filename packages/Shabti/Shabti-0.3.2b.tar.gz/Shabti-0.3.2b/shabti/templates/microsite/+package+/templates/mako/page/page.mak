# -*- coding: utf-8 -*-
## Based on standard 2-col Hide-Right derivation
## Defines "content" and "lhcolumn" fragments

<%inherit file="/core/hide-right.mak"/>
<%def name="header()">
    % if c.page.title is not UNDEFINED:
    <title>${c.page.title|n}</title>
    % else:
    <title>Bel-EPA :: Site map</title>
    % endif
</%def>
<%def name="content()">
                                ${c.content|n}
</%def>
<%def name="lhcolumn()">
    <%include file="../lhcolumn.mak" />
</%def>
