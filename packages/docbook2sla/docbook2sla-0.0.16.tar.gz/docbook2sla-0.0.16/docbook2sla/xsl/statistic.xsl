<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Statistics about Scribus sla files.

	$Date: 2008-03-03 12:26:29 +0100 (Mon, 03 Mar 2008) $
	$Revision: 192 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/statistic.xsl $

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="yes" encoding="UTF-8" />

	<xsl:template match="/">
		<xsl:variable name="PAGEOBJECTS" select="/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT" />
		<xsl:message>===================================================================</xsl:message>
		<xsl:message>STATISTICS:</xsl:message>
		<xsl:message>===================================================================</xsl:message>
		<xsl:message>ANZ. PAGEOBJECTS: <xsl:value-of select="count($PAGEOBJECTS)"/></xsl:message>
		<xsl:message></xsl:message>
		<xsl:message>===================================================================</xsl:message>
		<xsl:message>PAGEOBJECTS:</xsl:message>
		<xsl:message>===================================================================</xsl:message>
		<xsl:apply-templates select="/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT" />
	</xsl:template>

	<xsl:template match="PAGEOBJECT">
		<xsl:choose>
			<xsl:when test="@PFILE != ''">
				<xsl:message>BILD : '<xsl:value-of select="@ANNAME" />'</xsl:message>
			</xsl:when>
			<xsl:otherwise>
				<xsl:message>TEXT : '<xsl:value-of select="@ANNAME" />' </xsl:message>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:apply-templates select="ITEXT|para" />
	</xsl:template>

	<xsl:template match="ITEXT">
		<xsl:message>     +- ITEXT : '<xsl:value-of select="@CH" />'</xsl:message>
	</xsl:template>

	<xsl:template match="para">
		<xsl:message>     +- para  : '<xsl:value-of select="@PARENT" />'</xsl:message>
	</xsl:template>

</xsl:stylesheet>
