# -*- coding: utf-8 -*-
## Slog final template
## Based on standard 2-col Hide-Right derivation
## Defines "content" and "lhcolumn" fragments

<%inherit file="../hide-right.mak"/>
<%def name="content()">
                            <div id="content">
                                <h2>Server info for ${request.host}</h2>
                                <p>The URL you called: ${h.url()}</p>
                                <p>The name you set: ${c.name}</p>
                                <p>The server environment:<br />
                                <pre>${c.pretty_environ}</pre>
                                </p>
                            </div>
</%def>
<%def name="lhcolumn()">
                                <div id="latestnews">
                                </div>
</%def>




