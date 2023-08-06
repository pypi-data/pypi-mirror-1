# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>${c.title|n}</title>
    <link type="text/css" rel="stylesheet" href="/css/core/layout.css" media="screen" />
    <link type="text/css" rel="stylesheet" href="/css/core/presentation.css" media="print" />
    <link type="text/css" rel="stylesheet" href="/css/core/color.css" media="screen" />
    <link type="text/css" rel="stylesheet" href="/css/core/screen.css" media="screen" />
    <link type="text/css" rel="stylesheet" href="/css/thickbox.css" media="screen" />
</head>
<body>
    <div id="popup">
        <fieldset>
        <legend><span id="popuplegend">${c.title}</span></legend>
        <div id="popupcontent">${c.content if c.content else '<p>No Details available</p>'}</div>
        </fieldset>
    </div>
</body>
</html>