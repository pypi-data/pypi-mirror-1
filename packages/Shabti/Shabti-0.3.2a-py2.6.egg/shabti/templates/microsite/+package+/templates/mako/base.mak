# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<%namespace name="dublin_core" file="core/dublin_core.mak" import="*" />
<%namespace name="footer" file="core/footer.mak" import="*" />
<%namespace name="grddl" file="core/grddl.mak" import="*"/>
<%namespace name="headerblock" file="core/headerblock.mak" import="*" />
<%namespace name="jslibs" file="core/jslibs.mak" import="*" />
<%namespace name="meta" file="core/meta.mak" import="*" />
<%namespace name="rubric" file="core/rubric.mak" import="*" />
<%namespace name="signin" file="core/signin.mak" import="*" />
<%namespace name="styling" file="core/styling.mak" import="*" />
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head profile="http://www.w3.org/2003/g/data-view">
    <!-- Version 0.75 -->
    <!-- Design credit: usability and accessibility features based on http://www.usability.com.au -->
    <meta content="application/xhtml+xml; charset=UTF-8" http-equiv="content-type"/>
    ${meta.body()}
    ${grddl.body()}
    ${dublin_core.body()}
    ${jslibs.body()}
    ${styling.body()}
    ## On occasion it can be useful to
    ## be able to fulfil a js req from
    ## the controller's side.
    % if c.extra_js is not UNDEFINED:
    ${c.extra_js|n}
    % endif
    ## ditto for css
    % if c.extra_css is not UNDEFINED:
    ${c.extra_css|n}
    % endif
    ${self.header()}
</head>
<body>
    ## ${signin.body()}
    ${rubric.body()}
    ${headerblock.body()}
    ${next.body()}
    ${footer.body()}
</body>
</html>
