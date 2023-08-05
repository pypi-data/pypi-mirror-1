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
  <!-- Overrides atom templates for embedding RDFa -->
  <xsl:import href="util.xslt"/>  

  <xsl:template match="a:author[a:name]" mode="authorship">
    <span property="dc:creator">
      <xsl:value-of select="a:name"/>
    </span>
  </xsl:template>

  <xsl:template match="a:title" mode="feed-heading">
    <span property="rdfs:label"><xsl:value-of select="."/></span>    
  </xsl:template>  
  
  <xsl:template match="a:link" mode="entry-links">
    <a href="{@href}">
      <xsl:choose>
        <xsl:when test="@type"><xsl:value-of select="@type"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="concat('link',position())"/></xsl:otherwise>
      </xsl:choose>      
    </a>
    <xsl:if test="position() != last()">
      <xsl:text>, </xsl:text>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="a:entry">
    <div class="entry" about="{a:id}">
      <h1 
          property="rdfs:label" 
          content="{a:title}">
        <span style="text-decoration:underline"><xsl:value-of select="a:title"/></span>(<xsl:apply-templates select="a:link" mode="entry-links"/>)
      </h1>
      <div><span style="font-size: 8pt;font-weight:bold">Updated: </span><span class="updated" property="dc:date"><xsl:value-of select="a:updated"/></span></div>
      <div>
        <meta property="dcTerms:created" content="{a:published}"/>        
        <span style="font-size: 8pt;font-weight:bold"><xsl:text>Categories: </xsl:text></span>
        <span class="categories" property="dc:subject"><xsl:apply-templates select="a:category" mode="categories"/></span>
      </div>        
      <div><xsl:apply-templates/></div>
    </div>
  </xsl:template>    
</xsl:stylesheet>
