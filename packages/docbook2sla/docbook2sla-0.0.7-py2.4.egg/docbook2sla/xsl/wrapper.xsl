<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to include arbitrary xml code into a scribus wrapper
	document.

	Parameter: $secondinput (scribus pageobjects)

	$Date: 2008-03-04 07:48:30 +0100 (Di, 04 Mrz 2008) $
	$Revision: 197 $
	$URL: https://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/wrapper.xsl $

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="no" encoding="UTF-8" />

	<!--  -->
	<xsl:variable name="xmlcontent" select="document($secondinput)" />

	<!-- root -->
	<xsl:template match="/">
		<!-- make sure the input is correct -->
		<xsl:choose>
			<!-- test secondinput -->
			<xsl:when test="count($xmlcontent/PAGEOBJECTS/*)=1">
				<ERROR>Pageobjects nicht vorhanden!!!</ERROR>
			</xsl:when>
			<xsl:otherwise>
				<!-- apply all layout templates -->
				<xsl:apply-templates match="SCRIBUSUTF8NEW"/>
			</xsl:otherwise>
		</xsl:choose>

	</xsl:template>

	<!-- append the xml code to inject after the page node -->
	<xsl:template match="SCRIBUSUTF8NEW/DOCUMENT/PAGE">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
		<xsl:copy-of select="$xmlcontent/*/*" />

	</xsl:template>

	<xsl:template name="insert">
		<xsl:copy>
			<xsl:copy-of select="$xmlcontent" />
		</xsl:copy>
	</xsl:template>

	<!-- copy all nodes and attributes, except PAGEOBJECT nodes -->
	<xsl:template match="@*|*">
		<xsl:if test="name()!='PAGEOBJECT'">
			<xsl:copy>
				<xsl:apply-templates select="@*|node()"/>
			</xsl:copy>
		</xsl:if>
	</xsl:template>

</xsl:stylesheet>