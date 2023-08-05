<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:a="http://www.w3.org/2005/Atom"
  xmlns:xh="http://www.w3.org/1999/xhtml"
  xmlns:func="http://exslt.org/functions"
  xmlns:dyn="http://exslt.org/dynamic"
  xmlns:bc="http://brightcontent.net/ns/"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f func"
  exclude-result-prefixes="a xh dyn bc #default"
>

<!-- Use this once we have some sort of tidying mechanism
  <xsl:output method="xml" encoding="utf-8"
              doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
              doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>
-->
  <xsl:import href="../atom-rdfa.xslt"/>
  <xsl:output method="html" encoding="utf-8"/>
  <xsl:param name="bc:weblog-base-uri"/>
  <xsl:template match="a:feed">
    <html 
        xml:lang="en" 
        lang="en"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" 
        xmlns:v="http://www.w3.org/2001/vcard-rdf/3.0#" 
        xmlns:dc="http://purl.org/dc/elements/1.1/">
        <head>
            <title><xsl:value-of select="a:title"/></title>
        
        <!-- Use this once we have some sort of tidying mechanism
            <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
        -->
            <!-- GRDDL transform to extract RDFa (for clients that understand GRDDL but not RDFa directly) -->
            <link rel="transformation" href="http://www-sop.inria.fr/acacia/soft/RDFa2RDFXML.xsl" />            
            <meta name="generator" content="Bright Content"/>
            <link rel="stylesheet" type="text/css" media="screen,projection" href="static/naturalist/css/style.css" />
        </head>
        <body>
            
            <div id='page_wrapper'>
                
                <div id='page_header'>
                    <h1><xsl:apply-templates select="a:title" mode="feed-heading"/><xsl:apply-templates select="a:link[@type='application/atom+xml']" mode="atom-icon"/></h1>
                </div>
                
                <div id='menu_bar'>
                    
                    <div id="navcontainer">
                        <ul id="navlist">
                            <li id="active"><a id="current" href="http://www.brightcontent.net/" title="Bright Content">Bright Content</a></li>                        
                            <li><a href="http://metacognition.info" title="Chimezie Ogbuji - Metacognition">Template creator</a></li>
                            <li><a href="http://jigsaw.w3.org/css-validator/check/referer" title="This website contains valid CSS">Valid CSS</a></li>               
                        </ul>
                    </div>
                    
                </div>
                
                <div id='content_wrapper'>
                    
                    <div class='spacer'></div>                
                    <div id='left_side'>                    
                        <xsl:apply-templates/>                    
                    </div>                
                    <div class='spacer'></div>
                    
                </div>
                
                <div id='page_footer'>                
                    <p>
                        Copyright &#x00BB; 2006 <xsl:apply-templates  mode="authorship" select="a:author"/> |
                        Webdesign by <a href="http://www.designsbydarren.com/">Designs by Darren</a> | 
                        <a href="http://validator.w3.org/check/referer" title="XHTML 1.0 Strict">XHTML</a> | 
                        <a href="http://jigsaw.w3.org/css-validator/check/referer?warning=no&amp;profile=css2" title="CSS 2.0 Strict">CSS</a>                    
                    </p>                
                </div>
                
            </div>            
        </body>
    </html>
  </xsl:template>
  <xsl:template match="a:link" mode="atom-icon">
    <xsl:text>    </xsl:text><a href="{@href}"><img border="0" src="static/atom.png" alt="Atom Feed"/></a>
  </xsl:template>    
</xsl:stylesheet>
