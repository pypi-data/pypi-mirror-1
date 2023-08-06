# -*- coding: utf-8 -*-
<%def name="body()">
            <div id="srchbox">
                <div>
                    <form id="srchform" method="post" action="/search/">
                        <fieldset>
                            <legend><span>${_('Search')}</span></legend>
                            <input type="text" size="20" id="aq" name="aq"/>
                        </fieldset>
                    </form>
                </div>
            </div>
</%def>