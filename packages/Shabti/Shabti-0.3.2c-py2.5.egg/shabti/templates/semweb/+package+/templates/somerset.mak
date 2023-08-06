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
        var next = ${c.constituency};
        % else:
        var next = 9;
        % endif 
        var tl;
        function onTimeLine() {
            var eventSource = new Timeline.DefaultEventSource(0);
            
            var theme = Timeline.ClassicTheme.create();
            theme.event.bubble.width = 300;
            theme.event.bubble.height = 200;
            var d = Timeline.DateTime.setIso8601Date(new Date(), "2008-09-26");
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
            Timeline.loadXML("/rdflab/constituency_detail/"+next, function(xml, url) {
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
            <div id="layer0" class="rhsp"><span id="rubric"> ... South West UK constituency regions ... </span></div>
            <div id="_Taunton" class="rhsp"><table class="infobox geography vcard" style="width:300px;"> <tr> <th colspan="2" style="background-color:#efefef; text-align:center;"><big class="fn org"><b>Taunton</b></big><br /> <a href="http://en.wikipedia.org/wiki/County_constituency" title="County constituency" class="mw-redirect">County constituency</a></th> </tr> <tr> <td colspan="2" style="text-align:center;"><a href="http://en.wikipedia.org/wiki/Image:TauntonConstituency.svg" class="image" title="TauntonConstituency.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/TauntonConstituency.svg/120px-TauntonConstituency.svg.png" width="120" height="61" border="0" /></a><br /> <a href="http://en.wikipedia.org/wiki/Image:EnglandSomerset.svg" class="image" title="EnglandSomerset.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/2/21/EnglandSomerset.svg/120px-EnglandSomerset.svg.png" width="120" height="148" border="0" /></a></td> </tr> <tr> <td colspan="2" style="background-color:#efefef; text-align:center; font-weight:bold;">Taunton shown within <a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a>, and Somerset shown within <a href="http://en.wikipedia.org/wiki/England" title="England">England</a></td> </tr> <tr class="note"> <th>Created:</th> <td><a href="http://en.wikipedia.org/wiki/1295" title="1295">1295</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Jeremy_Browne" title="Jeremy Browne">Jeremy Browne</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/List_of_political_parties_in_the_United_Kingdom" title="List of political parties in the United Kingdom">Party</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Liberal_Democrats_(UK)" title="Liberal Democrats (UK)" class="mw-redirect">Liberal Democrat</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/United_Kingdom_constituencies" title="United Kingdom constituencies">Type</a>:</th> <td><a href="http://en.wikipedia.org/wiki/House_of_Commons_of_the_United_Kingdom" title="House of Commons of the United Kingdom">House of Commons</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Ceremonial_counties_of_England" title="Ceremonial counties of England">County</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/European_Parliament" title="European Parliament">EP constituency</a>:</th> <td><a href="http://en.wikipedia.org/wiki/South_West_England_(European_Parliament_constituency)" title="South West England (European Parliament constituency)">South West England</a></td> </tr> </table></div>
            <div id="_Bridgwater" class="rhsp"><table class="infobox geography vcard" style="width:300px;"> <tr> <th colspan="2" style="background-color:#efefef; text-align:center;"><big class="fn org"><b>Bridgwater</b></big><br /> <a href="http://en.wikipedia.org/wiki/County_constituency" title="County constituency" class="mw-redirect">County constituency</a></th> </tr> <tr> <td colspan="2" style="text-align:center;"><a href="http://en.wikipedia.org/wiki/Image:BridgwaterConstituency.svg" class="image" title="BridgwaterConstituency.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/8/86/BridgwaterConstituency.svg/120px-BridgwaterConstituency.svg.png" width="120" height="61" border="0" /></a><br /> <a href="http://en.wikipedia.org/wiki/Image:EnglandSomerset.svg" class="image" title="EnglandSomerset.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/2/21/EnglandSomerset.svg/120px-EnglandSomerset.svg.png" width="120" height="148" border="0" /></a></td> </tr> <tr> <td colspan="2" style="background-color:#efefef; text-align:center; font-weight:bold;">Bridgwater shown within <a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a>, and Somerset shown within <a href="http://en.wikipedia.org/wiki/England" title="England">England</a></td> </tr> <tr class="note"> <th>Created:</th> <td>1295, 1885</td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Ian_Liddell-Grainger" title="Ian Liddell-Grainger">Ian Liddell-Grainger</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/List_of_political_parties_in_the_United_Kingdom" title="List of political parties in the United Kingdom">Party</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Conservative_Party_(UK)" title="Conservative Party (UK)">Conservative</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/United_Kingdom_constituencies" title="United Kingdom constituencies">Type</a>:</th> <td><a href="http://en.wikipedia.org/wiki/House_of_Commons_of_the_United_Kingdom" title="House of Commons of the United Kingdom">House of Commons</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Ceremonial_counties_of_England" title="Ceremonial counties of England">County</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/European_Parliament" title="European Parliament">EP constituency</a>:</th> <td><a href="http://en.wikipedia.org/wiki/South_West_England_(European_Parliament_constituency)" title="South West England (European Parliament constituency)">South West England</a></td> </tr> </table></div>
            <div id="_Somerton and Frome" class="rhsp"><table class="infobox geography vcard" style="width:300px;"> <tr> <th colspan="2" style="background-color:#efefef; text-align:center;"><big class="fn org"><b>Somerton and Frome</b></big><br /> <a href="http://en.wikipedia.org/wiki/County_constituency" title="County constituency" class="mw-redirect">County constituency</a></th> </tr> <tr> <td colspan="2" style="text-align:center;"><a href="http://en.wikipedia.org/wiki/Image:SomertonFromeConstituency.svg" class="image" title="SomertonFromeConstituency.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/SomertonFromeConstituency.svg/120px-SomertonFromeConstituency.svg.png" width="120" height="61" border="0" /></a><br /> <a href="http://en.wikipedia.org/wiki/Image:EnglandSomerset.svg" class="image" title="EnglandSomerset.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/2/21/EnglandSomerset.svg/120px-EnglandSomerset.svg.png" width="120" height="148" border="0" /></a></td> </tr> <tr> <td colspan="2" style="background-color:#efefef; text-align:center; font-weight:bold;">Somerton and Frome shown within <a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a>, and Somerset shown within <a href="http://en.wikipedia.org/wiki/England" title="England">England</a></td> </tr> <tr class="note"> <th>Created:</th> <td><a href="http://en.wikipedia.org/wiki/1983" title="1983">1983</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a>:</th> <td><a href="http://en.wikipedia.org/wiki/David_Heath" title="David Heath">David Heath</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/List_of_political_parties_in_the_United_Kingdom" title="List of political parties in the United Kingdom">Party</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Liberal_Democrats_(UK)" title="Liberal Democrats (UK)" class="mw-redirect">Liberal Democrat</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/United_Kingdom_constituencies" title="United Kingdom constituencies">Type</a>:</th> <td><a href="http://en.wikipedia.org/wiki/House_of_Commons_of_the_United_Kingdom" title="House of Commons of the United Kingdom">House of Commons</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Ceremonial_counties_of_England" title="Ceremonial counties of England">County</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/European_Parliament" title="European Parliament">EP constituency</a>:</th> <td><a href="http://en.wikipedia.org/wiki/South_West_England_(European_Parliament_constituency)" title="South West England (European Parliament constituency)">South West England</a></td> </tr> </table></div>
            <div id="_Wells" class="rhsp"><table class="infobox geography vcard" style="width:300px;"> <tr> <th colspan="2" style="background-color:#efefef; text-align:center;"><big class="fn org"><b>Wells</b></big><br /> <a href="http://en.wikipedia.org/wiki/County_constituency" title="County constituency" class="mw-redirect">County constituency</a></th> </tr> <tr> <td colspan="2" style="text-align:center;"><a href="http://en.wikipedia.org/wiki/Image:WellsConstituency.svg" class="image" title="WellsConstituency.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WellsConstituency.svg/120px-WellsConstituency.svg.png" width="120" height="61" border="0" /></a><br /> <a href="http://en.wikipedia.org/wiki/Image:EnglandSomerset.svg" class="image" title="EnglandSomerset.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/2/21/EnglandSomerset.svg/120px-EnglandSomerset.svg.png" width="120" height="148" border="0" /></a></td> </tr> <tr> <td colspan="2" style="background-color:#efefef; text-align:center; font-weight:bold;">Wells shown within <a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a>, and Somerset shown within <a href="http://en.wikipedia.org/wiki/England" title="England">England</a></td> </tr> <tr class="note"> <th>Created:</th> <td>1295, 1885</td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a>:</th> <td><a href="http://en.wikipedia.org/wiki/David_Heathcoat-Amory" title="David Heathcoat-Amory">David Heathcoat-Amory</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/List_of_political_parties_in_the_United_Kingdom" title="List of political parties in the United Kingdom">Party</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Conservative_Party_(UK)" title="Conservative Party (UK)">Conservative</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/United_Kingdom_constituencies" title="United Kingdom constituencies">Type</a>:</th> <td><a href="http://en.wikipedia.org/wiki/House_of_Commons_of_the_United_Kingdom" title="House of Commons of the United Kingdom">House of Commons</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Ceremonial_counties_of_England" title="Ceremonial counties of England">County</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/European_Parliament" title="European Parliament">EP constituency</a>:</th> <td><a href="http://en.wikipedia.org/wiki/South_West_England_(European_Parliament_constituency)" title="South West England (European Parliament constituency)">South West England</a></td> </tr> </table></div>
            <div id="_Yeovil" class="rhsp"><table class="infobox geography vcard" style="width:300px;"> <tr> <th colspan="2" style="background-color:#efefef; text-align:center;"><big class="fn org"><b>Yeovil</b></big><br /> <a href="http://en.wikipedia.org/wiki/County_constituency" title="County constituency" class="mw-redirect">County constituency</a></th> </tr> <tr> <td colspan="2" style="text-align:center;"><a href="http://en.wikipedia.org/wiki/Image:YeovilConstituency.svg" class="image" title="YeovilConstituency.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/YeovilConstituency.svg/120px-YeovilConstituency.svg.png" width="120" height="61" border="0" /></a><br /> <a href="http://en.wikipedia.org/wiki/Image:EnglandSomerset.svg" class="image" title="EnglandSomerset.svg"><img alt="" src="http://upload.wikimedia.org/wikipedia/commons/thumb/2/21/EnglandSomerset.svg/120px-EnglandSomerset.svg.png" width="120" height="148" border="0" /></a></td> </tr> <tr> <td colspan="2" style="background-color:#efefef; text-align:center; font-weight:bold;">Yeovil shown within <a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a>, and Somerset shown within <a href="http://en.wikipedia.org/wiki/England" title="England">England</a></td> </tr> <tr class="note"> <th>Created:</th> <td>1918</td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a>:</th> <td><a href="http://en.wikipedia.org/wiki/David_Laws" title="David Laws">David Laws</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/List_of_political_parties_in_the_United_Kingdom" title="List of political parties in the United Kingdom">Party</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Liberal_Democrats_(UK)" title="Liberal Democrats (UK)" class="mw-redirect">Liberal Democrat</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/United_Kingdom_constituencies" title="United Kingdom constituencies">Type</a>:</th> <td><a href="http://en.wikipedia.org/wiki/House_of_Commons_of_the_United_Kingdom" title="House of Commons of the United Kingdom">House of Commons</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/Ceremonial_counties_of_England" title="Ceremonial counties of England">County</a>:</th> <td><a href="http://en.wikipedia.org/wiki/Somerset" title="Somerset">Somerset</a></td> </tr> <tr class="note"> <th><a href="http://en.wikipedia.org/wiki/European_Parliament" title="European Parliament">EP constituency</a>:</th> <td><a href="http://en.wikipedia.org/wiki/South_West_England_(European_Parliament_constituency)" title="South West England (European Parliament constituency)">South West England</a></td> </tr> </table></div>
            </div>
        <div id="svgbox">
${c.svg|n}
        </div>
    </div>
    <div id="tl" class="timeline-default timeline-container"></div>
    <div id="flashTransport">foobar</div>
    
</body>
</html>
