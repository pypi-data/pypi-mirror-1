<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:a="http://www.w3.org/2005/Atom"
  xmlns:xhtml="http://www.w3.org/1999/xhtml" 
  xmlns="http://www.w3.org/1999/xhtml" 
  exclude-result-prefixes="a xhtml">

  <xsl:output method="xml" encoding="utf-8"
              doctype-public="-//W3C//DTD XHTML 1.1//EN"
              doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>

  <xsl:template match="*"/><!-- Ignore unknown elements -->
  <xsl:template match="*" mode="links"/>
  <xsl:template match="*" mode="categories"/>

  <xsl:template match="a:feed">
<html xml:lang="en">
  <head>
    <title><xsl:value-of select="a:title"/></title>
  </head>
  <body>
    <h1><xsl:apply-templates select="a:title" mode="text-construct"/></h1>
    <xsl:apply-templates/>
    <p>Feed ID: <xsl:value-of select="a:id"/></p>
    <p>Feed updated: <xsl:value-of select="a:updated"/></p>
    <xsl:apply-templates/>
  </body>
</html>
  </xsl:template>

  <xsl:template match="a:summary">
    <div class="summary">
      <xsl:apply-templates select="." mode="text-construct"/>
    </div>
  </xsl:template>

  <xsl:template match="a:content">
    <div class="content">
      <xsl:apply-templates select="." mode="text-construct"/>
    </div>
  </xsl:template>

  <xsl:template match="a:entry">
    <div class="entry">
      <h2><xsl:apply-templates select="a:title" mode="text-construct"/></h2>
      <div class="id">Entry ID: <xsl:value-of select="a:id"/></div>
      <div class="updated">Entry updated: <xsl:value-of select="a:updated"/></div>
      <div class="links">
	<xsl:text/>Links: <xsl:apply-templates select="a:link" mode="links"/>
      </div>
      <div class="categories">
	<xsl:text>Categories: </xsl:text>
	<xsl:apply-templates select="a:category" mode="categories"/>
      </div>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="a:link" mode="links">
    <a href="{@href}">
      <xsl:value-of select="@rel"/>
      <xsl:if test="not(@rel)">[generic link]</xsl:if>
      <xsl:if test="@type">
	<xsl:text> (</xsl:text><xsl:value-of select="@type"/><xsl:text>): </xsl:text>
      </xsl:if>
      <xsl:value-of select="@title"/>
    </a>
    <xsl:if test="position() != last()">
      <xsl:text> | </xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="a:category" mode="categories">
    <xsl:value-of select="@term"/>
    <xsl:if test="position() != last()">
      <xsl:text> | </xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*[@type='text']|*[not(@type)]" mode="text-construct">
    <xsl:value-of select="node()"/>
  </xsl:template>

  <xsl:template match="*[@type='xhtml']" mode="text-construct">
    <xsl:copy-of select="node()"/>
  </xsl:template>

  <!-- Handle content elements with external data -->
  <xsl:template match="a:content[@src]" mode="text-construct">
    <!-- Use the XHTML object element -->
    <object data="{@src}" type="{@type}">Unable to render object</object>
  </xsl:template>

  <!-- Handle text media types for content elements -->
  <xsl:template
    match="a:content[not(@src)][starts-with(@type, 'text/')]"
    mode="text-construct">
    <xsl:value-of select="node()"/>
  </xsl:template>

  <!-- Handle XML media types for content elements -->
  <xsl:template
    match="a:content[not(@src)][substring-after(@type, '/') = 'xml'
           or starts-with(substring-after(@type, '/'), '+') = 'xml']"
    mode="text-construct">
    <!-- Just copy the XML over.  If mixed mode XHTML is not supported
         this might cause problems -->
    <xsl:copy-of select="node()"/>
  </xsl:template>

</xsl:stylesheet>
