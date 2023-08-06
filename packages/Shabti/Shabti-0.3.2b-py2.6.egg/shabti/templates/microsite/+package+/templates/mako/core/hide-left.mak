# -*- coding: utf-8 -*-
## Based on standard 3-col fluid tableless layout with left-hand column 
## suppressed.
## Inheriting template must define both "content" and "rhcolumn" fragments.

<%inherit file="../base.mak"/>
<%def name="header()">
    ${next.header()}
</%def>

<%def name="body()">
   <div id="main" class="hide-left">
        <div id="columns">
            <div class="cols-wrapper">
                <div class="float-wrapper">
                    <div id="col-a">
                        <div class="main-content">
                            <a id="contenttag">
                            </a>
                            <div id="content">
                                <!-- Content here -->
                                ${next.content()}
                            </div>
                        </div>
                    </div>
                </div>
                <div id="col-c" class="sidecol">
                    <div class="box">
                        <div id="rhcolumn">
                            <!-- Content here -->
                            ${next.rhcolumn() }
                        </div>
                    </div>
                </div>
                <div class="clear" id="em"></div>
            </div>
        </div>
    </div>
</%def>
