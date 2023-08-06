# -*- coding: utf-8 -*-
## Based on standard 3-col fluid tableless layout with left- and right-hand 
## columns suppressed.
## Inheriting template must define "content" fragment.

<%inherit file="../base.mak"/>
<%def name="header()">
    ${self.header()}
</%def>

<%def name="body()">
    <div id="main" class="hide-both">
        <div id="columns">
            <div class="cols-wrapper">
                <div class="float-wrapper">
                    <div id="col-a">
                        <div class="main-content">
                            <a id="contenttag">
                            </a>
                            <div id="content"  style="border-left:none; margin-left:0">
                                <!-- Content here -->
                                ${self.content()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</%def>

