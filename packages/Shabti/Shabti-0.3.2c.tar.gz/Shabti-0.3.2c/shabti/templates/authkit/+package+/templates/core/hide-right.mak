# -*- coding: utf-8 -*-
## Based on standard 3-col fluid tableless layout with right-hand column
## suppressed.
## Inheriting template must define both "content" and "lhcolumn" fragments.

<%inherit file="../base.mak"/>
<%def name="header()">
    ${next.header()}
</%def>

<%def name="body()">
    <div id="main" class="hide-right">
        <div id="columns">
            <div class="cols-wrapper">
                <div class="float-wrapper">
                    <div id="col-a">
                        <div class="main-content">
                            <a id="contenttag">
                            </a>
                            <div id="content">
                                <!-- Content here -->
                                ${self.content()}
                            </div>
                        </div>
                    </div>
                    <div id="col-b" class="sidecol">
                        <div class="box">
                             <div id="lhcolumn">
                               ${self.lhcolumn()}
                             </div>
                        </div>
                    </div>
                </div>
                <div class="clear" id="em"></div>
            </div>
        </div>
    </div>
</%def>
