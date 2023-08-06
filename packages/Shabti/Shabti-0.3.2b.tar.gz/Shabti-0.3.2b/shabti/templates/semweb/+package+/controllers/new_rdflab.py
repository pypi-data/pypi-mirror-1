# -*- coding: utf-8 -*-
from pylons import response, tmpl_context as c
from pylons.templating import render_mako
from foobar.lib.base import BaseController, config
from foobar.model.rdfmodel import *
import logging
log = logging.getLogger(__name__)

def get_wpedia_infobox(wpedialink):
    # Drat, we don't know the wpedialink for an MP until after
    # we get the results og the sparql query
    import commands
    data = commands.getoutput('wget -q -O - %s' % wpedialink)
    from lxml import etree
    parser = etree.XMLParser(remove_blank_text=True)
    wpediadoc = etree.XML(data, parser)
    print wpediadoc
    find = etree.XPath('''//h:div[@id="bodyContent"]/h:table[@class="infobox vcard"]''', namespaces={'h':'http://www.w3.org/1999/xhtml'})
    return etree.tostring(find(wpediadoc)[0])


# Eventually, scrape this off the wikipedia page using xpath
chunky = """\
<table class="infobox vcard" style="margin-top: 1px; width:23em; font-size:90%; text-align:left; padding-left:0.5em; padding-right:0.5em;">
    <tr>
        <td colspan="2" class="fn" style="text-align:center; font-size:140%; font-weight:bold;">
            <div class="imagemap-inline"><span class="fn">David Heathcoat-Amory</span>&#xA0;<span class="honorific-suffix" style="font-size:small;"><a href="http://en.wikipedia.org/wiki/Member_of_Parliament" title="Member of Parliament">MP</a></span></div>
        </td>
    </tr>
    <tr>
        <td colspan="2" style="text-align:center;">
            <a href="http://en.wikipedia.org/wiki/Image:David_Heathcoat-Amery.JPG" class="image" title="David Heathcoat-Amory">
                <img alt="David Heathcoat-Amory" src="http://upload.wikimedia.org/wikipedia/en/thumb/3/34/David_Heathcoat-Amery.JPG/150px-David_Heathcoat-Amery.JPG" width="150" height="205" border="0"/>
            </a>
            <br/>
        </td>
    </tr>
    <tr>
        <td colspan="2" style="text-align:center; font-size:110%;">
            <hr/>
            <div style="background:lavender; font-weight:bold;">Member of Parliament<br/> for <a href="http://en.wikipedia.org/wiki/Wells_(UK_Parliament_constituency)" title="Wells (UK Parliament constituency)">Wells</a></div>
        </td>
    </tr>
    <tr>
        <td colspan="2" style="text-align:center; background:lavender;">
            <b>
                <a href="http://en.wikipedia.org/wiki/Incumbent" title="Incumbent">Incumbent</a>
            </b>
        </td>
    </tr>
    <tr>
        <td colspan="2" style="text-align:center;"><b>Assumed&#xA0;office&#xA0;</b><br/>9 June 1983</td>
    </tr>
    <tr>
        <th>Preceded&#xA0;by</th>
        <td>
            <a href="http://en.wikipedia.org/wiki/Robert_Boscawen" title="Robert Boscawen">Robert Boscawen</a>
        </td>
    </tr>
    <tr>
        <th>Majority</th>
        <td>3,040 (5.7%)</td>
    </tr>
    <tr>
        <td colspan="2">
            <hr/>
        </td>
    </tr>
    <tr>
        <th>Born</th>
        <td>21 March 1949 <span style="display:none">(<span class="bday">1949-03-21</span>)</span> <span class="noprint">(age&#xA0;59)</span><br/></td>
    </tr>
    <tr>
        <th>Nationality</th>
        <td>
            <a href="http://en.wikipedia.org/wiki/United_Kingdom" title="United Kingdom">British</a>
        </td>
    </tr>
    <tr>
        <th>Political&#xA0;party</th>
        <td>
            <a href="http://en.wikipedia.org/wiki/Conservative_Party_(UK)" title="Conservative Party (UK)">Conservative</a>
        </td>
    </tr>
    <tr>
        <th>Spouse</th>
        <td>Linda Adams</td>
    </tr>
    <tr>
        <th>
            <a href="http://en.wikipedia.org/wiki/Alma_mater" title="Alma mater">Alma&#xA0;mater</a>
        </th>
        <td>
            <a href="http://en.wikipedia.org/wiki/Christ_Church,_Oxford" title="Christ Church, Oxford">Christ Church, Oxford</a>
        </td>
    </tr>
</table>
"""

class RdflabController(BaseController):

    def __before__(self):
        pass

    def index(self):
        try:
            rdfSubject.db = app_globals.graph
        except:
            rdfSubject.db = config['rdfalchemy.ra_engine']
        c.graph = rdfSubject.db
        return render_mako('default.mak')

    # def constituency(self, id=1010):
    # 
    #     # Imports
    #     from rdfalchemy.sparql.sesame2 import SesameGraph
    #     from rdflib import Namespace, URIRef, RDF, StringInputSource, Graph
    # 
    #     # Namespace declarations
    #     doap = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#doap')
    #     rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    #     foaf = Namespace('http://daml.umbc.edu/ontologies/cobra/0.4/foaf-basic#')
    #     ukpp = Namespace('http://bel-epa.com/ont/2007/6/ukpp.owl#')
    # 
    #     # Bind db URL and create the graph
    #     ukppdb = 'http://bel-epa.com:8080/openrdf-sesame/repositories/ukppsw01'
    #     db = SesameGraph(ukppdb)
    # 
    #     # Convenience bindings
    #     frmd = URIRef(ukpp['fromDate'])
    #     tod = URIRef(ukpp['toDate'])
    #     wp = URIRef(ukpp['wikipediaEntry'])
    #     fn = URIRef('http://daml.umbc.edu/ontologies/cobra/0.4/foaf-basic#name')
    # 
    #     # Specify the relationship we want to explore: ?mp reps ?y
    #     # The predicate ...
    #     reps = URIRef('http://reliant.teknowledge.com/DAML/SUMO.owl#represents')
    # 
    #     # Specify the constituency in which we are interested (?mp reps const)
    #     # The object ...
    #     constit = URIRef(ukpp['ukpp-const-%s' % id])
    # 
    #     # Find all triples where p,o matches the predicate and the object
    #     # (the semantics dictate that only an MP can rep a constit)
    #     # A (new, reduced) graph is returned 
    #     mps = db.value(None, reps, constit)
    # 
    #     # Iteratively, using the MPs retrieved, go back to the db
    #     # and retrieve all s, p, o where s is an MP, let p and o match
    #     # whatever's there
    #     for p, o in db.predicate_objects(mps):
    #         # Encode for convenience
    #         uo = o.encode('utf8')
    #         up = p.encode('utf8')
    #         # Keep what we want
    #         if p == tod:
    #             c.tod = uo
    #         elif p == frmd:
    #             c.frmd = uo
    #         elif p == fn:
    #             c.name = uo
    #         elif p == wp:
    #             c.wp = uo
    #     return render_mako('constituency.mak')

    def constituency(self, id=None):
        # log.debug("Called constituency")
        area_map = ['Avon', 'Cornwall', 'Devon', 'Dorset', 'Gloucestershire', 'Somerset', 'Wiltshire']
        response.headers['Content-Type'] = 'application/xhtml+xml; charset=utf-8'
        if not id:
            c.svg = ''.join(open('./foobar/public/maps/southwest.svg').readlines()[1:])
            c.clink = '/rdflab/constituency/Avon'
            tmpl = 'region'
        elif id in area_map:
            c.svg = ''.join(open('./foobar/public/maps/%s.svg' % id.lower()).readlines()[1:])
            c.clink = '/rdflab/constituency/%s' % id
            tmpl = id
        else:
            c.svg = ''.join(open('./foobar/public/maps/%s.svg' % id.lower()).readlines()[1:])
            c.clink = '/rdflab/constituency/%s' % id
            tmpl = 'region'
        c.ctitle = "%s constituencies." % id
        c.constituency = "   var next = %s;" % 0
        c.chunky = chunky
        return render_mako('%s.mak' % tmpl)
    
    def constituency_detail(self, id=458, **kwargs):
        # Ajax service
        try:
            from formencode import validators
            validator = validators.Int()
            id = validator.to_python(id)
        except Exception:
            log.debug("Excepting with %s [%s]" % (type(id), id))
            abort(404)

        from rdfalchemy.sparql.sesame2 import SesameGraph
        from rdflib import Namespace, URIRef, ConjunctiveGraph
        
        # Namespace declarations
        doap = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#doap')
        rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        foaf = Namespace('http://daml.umbc.edu/ontologies/cobra/0.4/foaf-basic#')
        ukpp = Namespace('http://bel-epa.com/ont/2007/6/ukpp.owl#')
        
        # Bind db URL and create the graph
        ukppdb = 'http://bel-epa.com:8080/openrdf-sesame/repositories/ukppsw01'
        db = SesameGraph(ukppdb)
        ns = dict(foaf=URIRef("http://daml.umbc.edu/ontologies/cobra/0.4/foaf-basic#"),
                  ukpp=URIRef("http://bel-epa.com/ont/2007/6/ukpp.owl#"),
                  rdf=URIRef("http://www.w3.org/2000/01/rdf-schema#"))

        # Query the graph for the constituency reference
        sparql_query = """SELECT ?ctitle ?clink
                            WHERE { 
                            ukpp:ukpp-const-%(cid)s rdf:label ?ctitle .
                            ukpp:ukpp-const-%(cid)s ukpp:wikipediaEntry ?clink}"""

        res = db.query(sparql_query % {'cid':id}, initNs=ns, 
                                        processor='sparql', 
                                        resultMethod='xml')
        (c.ctitle, c.clink) = res.next()

        # Now re-query 
        sparql_query = """SELECT ?title ?description ?end ?start ?link ?member
                            WHERE { 
                            ukpp:ukpp-const-%(cid)s ukpp:hasMemberOfParliament ?member .
                            ?member foaf:name ?title .
                            ?member ukpp:wikipediaEntry ?link .
                            ?member ukpp:parliamentaryRole ?role .
                            ?role ukpp:endingDate ?end .
                            ?role ukpp:startingDate ?start .
                            ?role ukpp:roleTaken ?taken .
                            ?taken ukpp:partyAffiliation ?affil .
                            ?affil rdf:comment ?description 
                            }
                            ORDER BY ?start"""
        res = db.query(sparql_query % {'cid':id}, initNs=ns, 
                                        processor='sparql', 
                                        resultMethod='xml',
                                        rawResults=True)
        # Want proper dates
        from datetime import datetime
        result = res.read().replace('9999-12-31', str(datetime.utcnow()))

        from lxml import etree
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.XML(result, parser)
        wpedialink = doc.find('{http://www.w3.org/2005/sparql-results#}results/result[0]/binding/[@name="link"]')
        from StringIO import StringIO
        f = StringIO('''\
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
            xmlns:sparql="http://www.w3.org/2005/sparql-results#"
            xmlns="http://www.w3.org/2005/sparql-results#"
            exclude-result-prefixes='xsl rdf sparql #default'>
              <xsl:output method="xml" indent="no" omit-xml-declaration="yes" encoding="UTF-8" />
            <xsl:template match="/">
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="sparql:sparql">
                <sparql><xsl:apply-templates/></sparql>
            </xsl:template>
            <xsl:template match="sparql:head">
                <head>
                    <variable name="isDuration"/>
                    <variable name="color"/>
                    <variable name="image"/>
                    <variable name="tapeImage"/>
                    <variable name="tapeRepeat"/>
                    <variable name="caption"/>
                    <variable name="classname"/>
                    <xsl:apply-templates/>
                </head>
            </xsl:template>
            <xsl:template match="sparql:result">
                <result>
                    <binding name="isDuration"><literal datatype="http://www.w3.org/2001/XMLSchema#boolean">true</literal></binding>
                    <binding name="color"><literal datatype="http://www.w3.org/2001/XMLSchema#String">%(color)s</literal></binding>
                    <binding name="tapeImage"><literal datatype="http://www.w3.org/2001/XMLSchema#String">/img/assets/blue_stripes.png</literal></binding>
                    <binding name="tapeRepeat"><literal datatype="http://www.w3.org/2001/XMLSchema#String">repeat-x</literal></binding>
                    <binding name="caption"><literal datatype="http://www.w3.org/2001/XMLSchema#String">Sitting MP</literal></binding>
                    <binding name="classname"><literal datatype="http://www.w3.org/2001/XMLSchema#String">hot_event</literal></binding>
                    <binding name="image"><literal datatype="http://www.w3.org/2001/XMLSchema#String">http://image.guardian.co.uk/sys-images/Politics/Pix/mps_/2001/03/20/david_heathcote_amory128.jpg</literal></binding>
                    <xsl:apply-templates/>
                </result>
            </xsl:template>
            <xsl:template match="sparql:binding">
                <binding name="{@name}"><xsl:apply-templates/></binding>
            </xsl:template>
            <xsl:template match="@*|node()">
                <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
            </xsl:template>
        </xsl:stylesheet>''' % {'color': 'blue', 'text':'Caption here.'}) # expand later
        xslt_doc = etree.parse(f)
        transform = etree.XSLT(xslt_doc)
        result = str(transform(doc))
        response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        return result
