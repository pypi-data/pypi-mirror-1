# -*- coding: utf-8 -*-
<%inherit file="/core/hide-both.mak"/>
<%def name="header()">
    % if c.title is not UNDEFINED:
    <title>${c.title or 'Index'}</title>
    % else:
    <title>shabtidemo :: Tabbed index</title>
    % endif
<script type="text/javascript" src="/js/tabber.js"></script>
<link type="text/css" rel="stylesheet" href="/css/tabber.css" media="screen" />
<script type="text/javascript">

/* Optional: Temporarily hide the "tabber" class so it does not "flash"
   on the page as plain HTML. After tabber runs, the class is changed
   to "tabberlive" and it will appear. */

document.write('<style type="text/css">.tabber{display:none;}<\/style>');

/*==================================================
  Set the tabber options (must do this before including tabber.js)
  ==================================================*/
var tabberOptions = {

  'cookie':"tabber", /* Name to use for the cookie */

  'onLoad': function(argsObj)
  {
    var t = argsObj.tabber;
    var i;

    /* Optional: Add the id of the tabber to the cookie name to allow
       for multiple tabber interfaces on the site.  If you have
       multiple tabber interfaces (even on different pages) I suggest
       setting a unique id on each one, to avoid having the cookie set
       the wrong tab.
    */
    if (t.id) {
      t.cookie = t.id + t.cookie;
    }

    /* If a cookie was previously set, restore the active tab */
    i = parseInt(getCookie(t.cookie));
    if (isNaN(i)) { return; }
    t.tabShow(i);
    //alert('getCookie(' + t.cookie + ') = ' + i);
  },

  'onClick':function(argsObj)
  {
    var c = argsObj.tabber.cookie;
    var i = argsObj.index;
    //alert('setCookie(' + c + ',' + i + ')');
    setCookie(c, i);
  }
};

/*==================================================
  Cookie functions
  ==================================================*/
function setCookie(name, value, expires, path, domain, secure) {
    document.cookie= name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires.toGMTString() : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");
}

function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    } else {
        begin += 2;
    }
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) {
        end = dc.length;
    }
    return unescape(dc.substring(begin + prefix.length, end));
}
function deleteCookie(name, path, domain) {
    if (getCookie(name)) {
        document.cookie = name + "=" +
            ((path) ? "; path=" + path : "") +
            ((domain) ? "; domain=" + domain : "") +
            "; expires=Thu, 01-Jan-70 00:00:01 GMT";
    }
}

</script>
<style type="text/css">
ul.list li {list-style-type:none;}
ul.list li a {text-decoration: none; font-size: 85%; line-height: 2em;}
</style>
</%def>
<%def name="content()">
    <h1>${c.title}</h1>
    <div class="tabber" style="margin: 0 0.5em; min-width:56em;">
        % for tabgroup in c.tabgroups:
        <div class="tabbertab" title="${h.literal(tabgroup['title'])}">
            <div class="namelist">
                <ul class="list col1">
                    % for link in tabgroup['group'][:len(tabgroup['group'])/3]:
                    <li>${h.literal(link)}</li>
                    % endfor
                </ul>
                <ul class="list col2">
                    % for link in tabgroup['group'][len(tabgroup['group'])/3:(len(tabgroup['group'])/3)*2]:
                    <li>${h.literal(link)}</li>
                    % endfor
                </ul>
                <ul class="list col3">
                    % for link in tabgroup['group'][(len(tabgroup['group'])/3)*2:]:
                    <li>${h.literal(link)}</li>
                    % endfor
                </ul>
            </div>
        </div>
        % endfor
    </div>
</%def>
<%def name="lhcolumn()">
</%def>
