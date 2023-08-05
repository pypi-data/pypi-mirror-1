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

  <xsl:import href="../util.xslt"/>

  <xsl:param name="bc:weblog-base-uri"/>

  <xsl:output method="html" encoding="utf-8"/>

  <!--xsl:param name="blogtitle" select="Weblog title"/-->

  <xsl:template match="a:feed">
<!-- Template from http://www.openwebdesign.org/viewdesign.phtml?id=2996&referer=%2F .  See readme.txt for more info -->
<html xml:lang="en" lang="en">
<head>
    <title><xsl:value-of select="a:title"/></title>
    <base href="{$bc:weblog-base-uri}"/>
<!-- Use this once we have some sort of tidying mechanism
    <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
-->
    
    <meta name="generator" content="Bright Content"/>
    <!--meta name="description" content="$blogdesc"/-->
    <!--meta name="keywords" content="good,keywords"/-->
    
    <!-- change the bluesky.css to bluesky_alt_<x>.css to change the default stylesheet to a alternative style -->
    <link rel="stylesheet" type="text/css" href="static/bluesky/css/bluesky.css" media="screen, tv, projection" title="Default" />
    
    <!-- alternative layouts (remove them if not wanted) -->
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_bright.css" media="screen, tv, projection" title="Alt 1: Bright style" />
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_handheld.css" media="screen, tv, projection" title="Alt 2: Handheld version" />
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_large.css" media="screen, tv, projection" title="Alt 3: Larger fonts" />
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_no_borders.css" media="screen, tv, projection" title="Alt 4: No borders" />
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_plain.css" media="screen, tv, projection" title="Alt 5: Plain layout" />
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/bluesky_alt_right_nav.css" media="screen, tv, projection" title="Alt 6: Right nav" />
   
   
    <link rel="alternative stylesheet" type="text/css" href="static/bluesky/css/print.css" media="screen" title="Print Preview" />
    
    <link rel="stylesheet" type="text/css" href="static/bluesky/css/handheld.css" media="handheld" title="Small Layout" />
    <link rel="stylesheet" type="text/css" href="static/bluesky/css/print.css" media="print" />

    <!-- Navigational metadata (an accessibility feature - preview in opera) -->
    <link rel="top" href="index.html" title="Homepage" />
    <link rel="up" href="index.html" title="Up" />
    <link rel="first" href="index.html" title="First page" />
    <link rel="previous" href="index.html" title="Previous page" />
    <link rel="next" href="index.html" title="Next page" />
    <link rel="last" href="index.html" title="Last page" />
    <link rel="toc" href="index.html" title="Table of contents" />
    <link rel="index" href="index.html" title="Site map" />
    
</head>
<body id="your-site-id">

<div id="page">
    
    <div id="header">
        <a href="."><xsl:apply-templates select="a:title" mode="text-construct"/></a>
    </div>
    
    <div id="wrapper"> 
        <div id="content">
            <div id="path">
                You are here: <a href="index.html">Home</a> 
                &#x00BB; <a href="index.html">Weblog</a>
            </div>
    
            <div id="main">
      <xsl:apply-templates/>

<!--
    <p>Feed ID: <xsl:value-of select="a:id"/></p>
    <p>Feed updated: <xsl:value-of select="a:updated"/></p>


                <h1><xsl:value-of select="$blogtitle"/></h1>
    
                <p>
                    Hello, this is my first free template I made.
                    I called it <i>blue sky</i> because of the colors I used. It is 100% compliant with XHTML 1.0 
                    Strict and does not contain any tables. I also tried to use relative metrics
                    everywhere, so the layout should be very flexible (scaling, resizing, font sizes, etc.). 
                    Further, I also included three different stylesheets (print layout, handheld, larger fonts).
                    I would be very happy about some feedback! <i>- Jonas John</i>
                </p>
    

                <div class="img_left">
                    <img src="images/img1.jpg" width="150" height="110" alt="put a good photo description in here" />
                </div>
                
                <p>
                    The source code (HTML and CSS) should be tidy and easy to to customize. 
                    I tested the design successfully in <a href="http://www.mozilla.org/">Mozilla Firefox 1.5</a>, 
                    <a href="http://www.opera.com/">Opera 9.0</a> and Internet Explorer 6.0. Some parts of the CSS code and the
                    XHTML structure were inspired by the layouts of <a href="http://www.oswd.org/user/profile/id/3013">haran</a> - 
                    thanks for the great work!
                </p>
                    
                <br />
-->
            </div>
        </div>
        
        <div id="left">
            <div id="nav">
                <h3>Navigation</h3>
                <div class="inner_box">
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/?">About</a></li>
                    </ul>                
                </div>
            </div>
            <div class="left_box">
                <h3>A Bright COntent Weblog</h3>
                <div class="inner_box">
                    <p>
                        This Weblog was brought to you by <div><a href="http://brightcontent.net/blog/">Bright Content</a>,  Python Weblog software built from reusable components.</div>
                        <a href="http://brightcontent.net/blog/">Learn more...</a>
                    </p>
                </div>
            </div>
            <div class="left_box">
                <h3>Links</h3>
                <div class="inner_box">
                    <p>
                        <ul>
			  <li><a href="http://www.brightcontent.net/" title="Bright Content Home">Bright Content Home</a></li>
			  <li><a href="http://www.brightcontent.net/" title="Bright Content project page">Bright Content project page</a></li>
                          <li><a href="http://www.jonasjohn.de/" title="Personal homepage of Jonas John">Template creator</a></li>
                          <li><a href="http://www.openwebdesign.org/" title="Open Source Web Design">OWD.org</a></li>
<!--
                          <li><a href="http://validator.w3.org/check/referer" title="This website is compliant with XHTML Strict 1.0">Valid XHTML</a></li>
-->
                          <li><a href="http://jigsaw.w3.org/css-validator/check/referer" title="This website contains valid CSS">Valid CSS</a></li>
			</ul>
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <div id="footer">
        <p>
            Copyright &#x00BB; 2006 <a href="index.html"><xsl:value-of select="a:author/a:name"/></a>. 
            <!-- Please do not remove the following credit to the Web designer -->
            Webdesign by <a href="http://www.jonasjohn.de/">Jonas John</a>. 
            
        </p>
    </div>
</div>

</body>
</html>
  </xsl:template>

</xsl:stylesheet>
