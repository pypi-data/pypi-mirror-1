<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to merge complex pageobjects.

	$Date: 2008-03-03 12:26:29 +0100 (Mon, 03 Mar 2008) $
	$Revision: 192 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/merge_complex_pageobjects.xsl $

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- ################################################################################################# -->
  <!-- ### COMPLEX PAGE OBJECTS                                                                      ### -->
  <!-- ################################################################################################# -->

  <!-- PAGEOBJECTS WITH ITEXT Nodes -->
  <xsl:template match="PAGEOBJECT[@ANNAME='text']">
    <xsl:message>COMPLEX PAGEOBJECT "<xsl:value-of select="@ANNAME"/>" FOUND:</xsl:message>
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:apply-templates select="$content/book/article/para|$content/book/article/bridgehead"
                           mode="complex-pageobject" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="para" mode="complex-pageobject">

    <!-- create ITEXT node -->
    <xsl:element name="ITEXT">
      <xsl:attribute name="CH">
        <xsl:value-of select="." />
      </xsl:attribute>
      <xsl:attribute name="SHORTCUT"></xsl:attribute>
      <xsl:attribute name="CNAME"></xsl:attribute>
      <xsl:message>  +-ITEXT node created</xsl:message>
    </xsl:element>

    <!-- create para node -->
    <!-- <para PSHORTCUT="" SHORTCUT="" CNAME="" NAME="" /> -->
    <xsl:element name="para">
      <xsl:attribute name="PSHORTCUT"></xsl:attribute>
      <xsl:attribute name="SHORTCUT"></xsl:attribute>
      <xsl:attribute name="CNAME"></xsl:attribute>
      <xsl:attribute name="PARENT">Standard-Absatzstil</xsl:attribute>
      <xsl:message>  +-para node created</xsl:message>
    </xsl:element>

  </xsl:template>

  <xsl:template match="bridgehead" mode="complex-pageobject">
    <!-- create ITEXT node -->
    <xsl:element name="ITEXT">
      <xsl:attribute name="ANNAME">
        <xsl:value-of select="@*" />
      </xsl:attribute>
      <xsl:attribute name="CH">
        <xsl:value-of select="." />
      </xsl:attribute>
      <xsl:message>  +-ITEXT node created</xsl:message>
    </xsl:element>

    <!-- create para node -->
    <xsl:element name="para" xsl:use-attribute-sets="PARA-Node">
      <xsl:attribute name="PARENT">Standard-Zwischenueberschriftstil</xsl:attribute>
      <xsl:message>  +-para node created</xsl:message>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>