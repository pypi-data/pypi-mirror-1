#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201
"""

doapfiend_html
==============

This is a plugin for formatting DOAP as HTML.

"""


import logging
from cStringIO import StringIO
#from pkg_resources import resource_string

from lxml import etree

from doapfiend.plugins.base import Plugin

__docformat__ = 'epytext'

#HDOAP_XSL = resource_string(__name__, "doap2html.xsl")
LOG = logging.getLogger(__name__)


def make_html(doap_xml):
    '''
    Create HTML page from DOAP profile

    @param doap_xml: DOAP in RDF/XML serialization
    @type doap_xml: string

    @rtype: string
    @returns: DOAP in HTML

    '''
    transform = etree.XSLT(etree.parse(open(HDOAP_XSL)))
    doc = etree.fromstring(doap_xml)
    result_tree = transform(doc)
    out = StringIO()
    out.write("")
    try:
        #Older version of lxml, make compatible?
        #result_tree.write(out, 'utf-8')
        result_tree.write(out)
    except AssertionError:
        LOG.error("Invalid RDF")
        return
    text = out.getvalue()
    out.close()
    return text


class HtmlPlugin(Plugin):

    """Class for formatting DOAP output"""

    name = "html"
    enabled = False
    enable_opt = None

    def __init__(self):
        '''Setup HtmlPlugin class'''
        super(HtmlPlugin, self).__init__()
            
    def add_options(self, parser, output, search):
        '''Add plugin's options to doapfiend's opt parser'''
        output.add_option('--%s' % self.name,
                action='store_true', 
                dest=self.enable_opt,
                help='Display DOAP as HTML')
        return parser, output, search

    def serialize(self, doap_xml, color=False):
        '''
        Serialize DOAP as HTML

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: string

        @param color: Does nothing, could toggle CSS
        @type color: boolean 

        @rtype: unicode
        @returns: DOAP as HTML

        '''
        return make_html(doap_xml)

HDOAP_XSL = '''
<!-- 

Author: Danny Ayers
http://dannyayers.com:88/xmlns/hdoap/profile/index.xhtml

Modified by Rob Cakebread <rob <@> doapspace.org>:

 09-13-2007 Added:
	file-release
	old-homepage
	screenshots
	programming-language
	wiki
	bug-database
	os
	helper
	developer
	documenter
	translator
	tester
 04-23-2008
    shortname
-->
<xsl:stylesheet version="1.0" 
				xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
				xmlns="http://www.w3.org/1999/xhtml"
				xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
				xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
				xmlns:dc="http://purl.org/dc/elements/1.1/"
				xmlns:foaf="http://xmlns.com/foaf/0.1/"
				xmlns:doap="http://usefulinc.com/ns/doap#"
				>
  
  <xsl:output method="xml" indent="yes" encoding="utf-8" />
  
  <xsl:template match="/"> 
	<xsl:apply-templates select="/rdf:RDF/doap:Project|/doap:Project" />
  </xsl:template> 
  
  <xsl:template match="/rdf:RDF/doap:Project|/doap:Project"> 
	<html>
	  <head profile="http://purl.org/stuff/hdoap/profile">
		<title><xsl:value-of select="doap:name/text()"/></title>
		<link rel="transformation" href="http://purl.org/stuff/hdoap/hdoap2doap.xsl" />  
		<link href="/static/css/hdoap.css" rel="stylesheet" type="text/css" />	  
	  </head>
	  <body>
		<div class="Project">
		  <h1>Project: <xsl:value-of select="doap:name/text()"/></h1>
		  <div class="project-details">
			<xsl:apply-templates select="*[count(*)=0]" />
		  </div>
		  <xsl:apply-templates select="doap:release"/>
		  <xsl:apply-templates select="doap:repository" />
		  <xsl:apply-templates select="doap:maintainer" />
		  <xsl:apply-templates select="doap:developer" />
		  <xsl:apply-templates select="doap:documenter" />
		  <xsl:apply-templates select="doap:translator" />
		  <xsl:apply-templates select="doap:tester" />
		  <xsl:apply-templates select="doap:helper" />
		</div>
		<xsl:apply-templates select="/rdf:RDF/rdf:Description" /> 
	  </body>
	</html>
  </xsl:template>
  
  <!--  Properties with Literal subjects -->
  <xsl:template match="doap:name|doap:shortname|doap:created|doap:programming-language|doap:shortdesc|doap:description|doap:revision|foaf:name|foaf:mbox_sha1sum|doap:anon-root|doap:module|doap:os">
	<p>
	  <span class="literal-label"><xsl:value-of select="local-name()" /></span> :  
	  <span class="literal-value">
		<xsl:attribute name="class"><xsl:value-of select="local-name()" /></xsl:attribute>
		<xsl:if test="@xml:lang">
		  <xsl:attribute name="xml:lang"><xsl:value-of select="@xml:lang" /></xsl:attribute>
		</xsl:if> 
		<xsl:value-of select="text()" />
	  </span>
	</p>
  </xsl:template>
  
  <!-- Properties with Resource subjects -->
  <xsl:template match="doap:homepage|doap:old-homepage|doap:file-release|doap:mailing-list|doap:download-page|doap:download-mirror|doap:bug-database|doap:category|doap:license|rdfs:seeAlso|doap:location|doap:browse|foaf:mbox|foaf:homepage|doap:wiki|doap:screenshots">
	<p>
	  <span class="resource-label"><xsl:value-of select="local-name()" /></span> :  
	  <span class="resource-value">
	  <a>
		<xsl:attribute name="class"><xsl:value-of select="local-name()" /></xsl:attribute>
		<xsl:attribute name="href"><xsl:value-of select="@rdf:resource" /></xsl:attribute>
		<xsl:value-of select="@rdf:resource" />  
	  </a>
	  </span>
	</p>
  </xsl:template>
  
  <!-- Release subsection -->
  <xsl:template match="doap:release">
	<div class="release">
	  <h2>Release</h2>
	  <div class="Version">
		<xsl:apply-templates select="./doap:Version/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Maintainer subsection -->
  <xsl:template match="doap:maintainer">
	<div class="maintainer">
	  <h2>Maintainer</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Developer subsection -->
  <xsl:template match="doap:developer">
	<div class="developer">
	  <h2>Developer</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Documenter subsection -->
  <xsl:template match="doap:documenter">
	<div class="documenter">
	  <h2>Documenter</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Translator subsection -->
  <xsl:template match="doap:translator">
	<div class="translator">
	  <h2>Translator</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>

  <!-- Tester subsection -->
  <xsl:template match="doap:tester">
	<div class="tester">
	  <h2>Tester</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Helper subsection -->
  <xsl:template match="doap:helper">
	<div class="helper">
	  <h2>Helper</h2>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>

  <!-- Repository subsection -->
  <xsl:template match="doap:repository">
	<div class="repository">
	  <h2>Repository</h2>
	  <div>
		<xsl:attribute name="class"><xsl:value-of select="local-name(./*)"/></xsl:attribute>
		<xsl:apply-templates select="./*/*" />
	  </div>
	</div>
  </xsl:template>
  
  <!-- Maker subsection -->
  <xsl:template match="/rdf:RDF/rdf:Description/foaf:maker">
	<div class="maker">
	  <h3>Maker of DOAP Profile</h3>
	  <div class="Person">
		<xsl:apply-templates select="./foaf:Person/*" />
	  </div>
	</div>
  </xsl:template>
  
</xsl:stylesheet>
'''
