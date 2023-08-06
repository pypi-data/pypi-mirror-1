# -*- coding: utf-8 -*-
<%def name="body()">
    <!-- Dublin Core metadata statements -->
    % if c.dcmeta.description is not UNDEFINED:
    <meta name="Description" content="${c.dcmeta.description}" />
    % endif
    % if c.dcmeta.title is not UNDEFINED:
    <meta name="DC.title" content="${c.dcmeta.title}|h" />
    % endif
    <meta name="Distribution" content="c.dcmeta.distribution" />
    <link href="http://purl.org/dc/elements/1.1/" rel="schema.DC" />
    <link href="http://purl.org/dc/terms/" rel="schema.DCTERMS" />
    <meta name="DC.Creator" content="${c.dcmeta.creator}" />
    <meta name="DC.Rights" content="${c.dcmeta.copyright}, ${c.dcmeta.copyrightyear}" />
    <meta name="DC.Date" content="${c.dcmeta.date}" />
    % if c.dcmeta.identifier is not UNDEFINED:
    <meta name="DC.Identifier" content="${c.dcmeta.identifier}" scheme="DCTERMS.URI" />
    % endif
    <meta name="DC.format" content="text/html" scheme="DCTERMS.IMT" />
    <meta name="DC.type" content="Text" scheme="DCTERMS.DCMIType" />
    % if c.dcmeta.abstract is not UNDEFINED:
    <meta name="DCTERMS.abstract" content="${c.dcmeta.abstract}" />
    % endif
    % if c.dcmeta.issued is not UNDEFINED:
    <meta name="DCTERMS.issued" content="${c.dcmeta.issued}" scheme="DCTERMS.W3CDTF" />
    % endif
    <meta name="ICBM" content="${c.dcmeta.icbm}" />
</%def>
