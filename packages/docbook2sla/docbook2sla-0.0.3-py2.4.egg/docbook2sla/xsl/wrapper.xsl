<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to include arbitrary xml code into a scribus wrapper
	document.

	Version 0.1
	2008/02/25
	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="no" encoding="UTF-8" />

	<!--  -->
	<xsl:variable name="xmlcontent" select="document($content)" />

	<!-- root -->
	<xsl:template match="/">
		<!-- apply all layout templates -->
		<xsl:apply-templates match="SCRIBUSUTF8NEW"/>
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