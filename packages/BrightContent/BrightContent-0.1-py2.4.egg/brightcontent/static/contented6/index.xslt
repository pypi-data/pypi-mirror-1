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
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:dcTerms="http://purl.org/dc/terms/">
        <head>
            <title><xsl:value-of select="a:title"/></title>
        
        <!-- Use this once we have some sort of tidying mechanism
            <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
        -->
            <!-- GRDDL transform to extract RDFa (for clients that understand GRDDL but not RDFa directly) -->
            <link rel="transformation" href="http://www-sop.inria.fr/acacia/soft/RDFa2RDFXML.xsl" />   
            <meta name="generator" content="Bright Content"/>
            <link rel="stylesheet" type="text/css" media="screen,projection" href="static/contented6/css/style.css" />
        </head>        
        <body>            
            <div id="header">                
                <div id="title"><xsl:apply-templates select="a:title" mode="feed-heading"/><xsl:apply-templates select="a:link[@type='application/atom+xml']" mode="atom-icon"/></div>
                <ul id="nav">                    
                    <li><a href="http://metacognition.info" title="Chimezie Ogbuji - Metacognition">Template creator</a></li>
                    <li><a href="http://www.brightcontent.net/" title="Bright Content">Bright Content</a></li>
                    <li><a href="http://jigsaw.w3.org/css-validator/check/referer" title="This website contains valid CSS">Valid CSS</a></li>               
                </ul>
            </div> <!-- end header -->
            <!--
                Uncommenting the following div will display a "slogan" inside the
                narrow blue horizontal line just beneath the header. You can use this
                area to display a company slogan, contact information, or a phrase
                that sets the mood for the page. The area will expand its height to
                fit the text.
            -->
            <!--
                <div id="slogan">
                Contented: How a content-filled design feels
                </div>
            -->
            <div id="content">
                <div id="maincontent">        
                    <xsl:apply-templates/>                    
                </div> <!-- end maincontent -->
                <div id="sidecontent">
                    <h2>News</h2>
                    Optional text introducing news items.
                    <ul>
                        <li><a href="#"> News item link 1</a> (May 15, 2006)</li>
                        <li><a href="#"> News item link 2</a> (May 12, 2006)</li>
                        <li><a href="#"> News item link 3</a> (May 7, 2006)</li>
                        
                    </ul>
                    <h2>Links</h2>
                    Optional text introducing links.
                    <ul>
                        <li><a href="#"> Related link 1</a></li>
                        
                        <li><a href="#"> Related link 2</a></li>
                    </ul>
                    <h2>Resources</h2>
                    Optional text introducing help.
                    <ul>
                        <li><a href="#">Download link 1</a></li>
                    </ul>
                    <div id="nullblock"></div>
                </div> <!-- end sidecontent -->
            </div> <!-- end content -->
            <div id="footer">
                
                <div id="copyrightdesign">
                    <p>
                        Copyright &#x00BB; 2006 <xsl:apply-templates  mode="authorship" select="a:author"/> |
                            Webdesign by <a href="http://ContentedDesigns.com">Contented Designs</a> | 
                        <a href="http://validator.w3.org/check/referer" title="XHTML 1.0 Strict">XHTML</a> | 
                        <a href="http://jigsaw.w3.org/css-validator/check/referer?warning=no&amp;profile=css2" title="CSS 2.0 Strict">CSS</a>                    
                    </p>                
                </div>                
                <div id="footercontact">
                    <a href="#">Contact</a>
                </div>                
            </div>            
        </body>        
    </html>
  </xsl:template>
  <xsl:template match="a:link" mode="atom-icon">
    <xsl:text>    </xsl:text><a href="{@href}"><img border="0" src="static/atom.png" alt="Atom Feed"/></a>
  </xsl:template>
</xsl:stylesheet>
