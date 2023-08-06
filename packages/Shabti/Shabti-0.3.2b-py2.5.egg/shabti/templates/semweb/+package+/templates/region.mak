<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" 
      xmlns:svg="http://www.w3.org/2000/svg"
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:cc="http://creativecommons.org/ns#"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
      xml:lang="en" lang="en">
<head>
    <script>
        Timeline_ajax_url="/javascripts/simile/ajax/api/simile-ajax-api.js";
        Timeline_urlPrefix='/javascripts/simile/timeline/api/';       
        Timeline_parameters='defaultLocale=en';
    </script>

    <script src="/javascripts/simile/timeline/api/timeline-api.js?bundle=false" type="text/javascript"></script> 
	<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"/>
	<title>${c.ctitle|n}</title>
	<script type="text/javascript" src="/javascripts/simile/ajax/api/scripts/jquery-1.2.6.js"/>
	<script type="text/javascript" src="/javascripts/jquery.tooltip.js"/>
    <link rel="stylesheet'" href="/css/styles.css" type='text/css' />

    <style type="text/css">
    #rhs {padding: 0 0.5em; float:right; width:320px; height:490px; border:1px solid #aaa}
    #rhs h2 {padding: 0 0.25em; font-style:italic; font-weight:normal;}
    #rhs p {padding: 0 0.25em;}
    #rubric {font-family:Helvetica; font-style:italic; padding:0 2em;}
    h1.mainh1 {font-size:120%; font-weight:bold; padding: 0.25em; margin:0.25em;}
    #svgbox {
        margin:0.33 0; padding:5px; width:640px; height:480px; border:1px solid #aaa; max-width:640px;
    }
    #tl {height: 250px; width:1000px;}
    #flashTransport {clear:all; float:none; visibility:hidden; }
    .rhsp {visibility:hidden; position: absolute; font-size: 90%}
    .rhsp a {text-decoration: none;}
    #layer0 {visibility:visible;}
    </style>
    <script type="text/javascript"> 
        $('g > path').tooltip({
    	track: true,
    	delay: 0,
    	bodyHandler: function() {
    		return $($(this).attr("id"));
    	},
    	showURL: false,
    	fade: 250 });
        % if c.constituency is DEFINED:
        var next1 = ${c.constituency};
        % else:
        var next1 = 616;
        % endif 
        var tl;
        function original_onTimeLine() {
            var eventSource = new Timeline.DefaultEventSource(0);
            
            var theme = Timeline.ClassicTheme.create();
            theme.event.bubble.width = 300;
            theme.event.bubble.height = 200;
            var d = Timeline.DateTime.setIso8601Date(new Date(), "2008-10-03");
            var bandInfos = [
                Timeline.createBandInfo({
                    width:          "80%", 
                    intervalUnit:   Timeline.DateTime.DAY, 
                    intervalPixels: 100,
                    eventSource:    eventSource,
                    date:           d,
                    theme:          theme
                }),
                Timeline.createBandInfo({
                    width:          "10%", 
                    intervalUnit:   Timeline.DateTime.MONTH, 
                    intervalPixels: 150
                }),
                Timeline.createBandInfo({
                    width:          "10%", 
                    intervalUnit:   Timeline.DateTime.YEAR, 
                    intervalPixels: 200
                })
            ];
            bandInfos[1].syncWith = 0;
            bandInfos[1].highlight = true;            
            bandInfos[2].syncWith = 1;
            bandInfos[2].highlight = true;            
 
            tl = Timeline.create(document.getElementById("tl"), bandInfos, Timeline.HORIZONTAL);
            Timeline.loadXML("/rdflab/constituency_detail/"+next1, function(xml, url) {
                eventSource.loadSPARQL(xml, url);
            });
        }
        function onTimeLine() {
            var eventSource = new Timeline.DefaultEventSource(0);
            
            var theme = Timeline.ClassicTheme.create();
            theme.event.bubble.width = 300;
            theme.event.bubble.height = 200;
            var d = Timeline.DateTime.setIso8601Date(new Date(), "2008-10-03");
            var bandInfos = [
                Timeline.createBandInfo({
                    width:          "70%", 
                    intervalUnit:   Timeline.DateTime.YEAR, 
                    intervalPixels: 80,
                    eventSource:    eventSource,
                    date:           d,
                    trackHeight:    1.5,
                    label:          "Representing MP",
                    theme:          theme
                }),
                Timeline.createBandInfo({
                    width:          "30%", 
                    intervalUnit:   Timeline.DateTime.DECADE, 
                    intervalPixels: 200
                }),
            ];
            bandInfos[1].syncWith = 0;
            bandInfos[1].highlight = true;            
 
            tl = Timeline.create(document.getElementById("tl"), bandInfos, Timeline.HORIZONTAL);
            Timeline.loadXML("/rdflab/constituency_detail/"+next1, function(xml, url) {
                eventSource.loadSPARQL(xml, url);
            });
        }
        var resizeTimerID = null;
        function onResize() {
            if (resizeTimerID == null) {
                resizeTimerID = window.setTimeout(function() {
                    resizeTimerID = null;
                    tl.layout();
                }, 500);
            }
        }
    </script> 
	<script type="text/javascript" src="/javascripts/lib.js"/>
</head>

<body>
    <h1 class="mainh1">
    % if c.clink is not UNDEFINED:
        <a href="/rdflab/constituency">South West UK</a> :: <a href="${c.clink}">${c.ctitle|n}</a>
    % else:
        <a href="/rdflab/constituency">South West UK</a> ${':: ' + c.ctitle if c.title else ''|n}
    % endif
    </h1>
    <div style="width:1000px">
        <div id="rhs">
            <div id="layer0" class="rhsp"><span id="rubric"> 
                %if c.chunky is not UNDEFINED:
                ${c.chunky|n}
                % else:
                ... South West UK constituency regions ...
                % endif 
                </span>
            </div>
                
        </div>
        <div id="svgbox">
${c.svg|n}
        </div>
    </div>
    <div id="tl" class="timeline-default timeline-container"></div>
    <div id="flashTransport">foobar</div>
    
</body>
</html>
