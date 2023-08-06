<%namespace name="searchform" file="searchform.mak" import="*"/>
<%def name="body()">
    <div id="header">
        <div id="logo">
            <h1 id="invisihead" class="displaynone">${'AuthK'}</h1>
            ##${searchform.body()}
        </div>
        <ul id="skipnav">
            <li><a href="#/core/navarea.htmltag">${'Skip to area navigation'}</a></li>
            <li><a href="#contenttag">${'Skip to content'}</a></li>
        </ul>
        <div id="legend">
            ##<p>${_('Crisp summary here')}</p>
        </div>
    </div>
</%def>