<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to merge simple pageobjects.

	$Date: 2008-03-03 12:26:29 +0100 (Mon, 03 Mar 2008) $
	$Revision: 192 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/merge_simple_pageobjects.xsl $

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- ################################################################################################# -->
  <!-- ### TITLE                                                                                     ### -->
  <!-- ################################################################################################# -->

  <xsl:template match="PAGEOBJECT[@ANNAME='title']/ITEXT">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:attribute name="CH">
        <xsl:apply-templates select="$content/book/article/title" />
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>

  <!-- ################################################################################################# -->
  <!-- ### SUBTITLE                                                                                  ### -->
  <!-- ################################################################################################# -->

  <xsl:template match="PAGEOBJECT[@ANNAME='subtitle']/ITEXT">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:attribute name="CH">
        <xsl:apply-templates select="$content/book/article/subtitle" />
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>

  <!-- ################################################################################################# -->
  <!-- ### BLOCKQUOTE                                                                                ### -->
  <!-- ################################################################################################# -->

  <xsl:template match="PAGEOBJECT[@ANNAME='blockquote']/ITEXT">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:attribute name="CH">
        <xsl:apply-templates select="$content/book/article/blockquote/para" />
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>