<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to syncronise the content of a DocBook file with an existing
	Scribus file.

	This stylesheets only works if there is a corresponding scribus
	pageobject to every docbook node!!!

	Parameter: $content

	$Date:2008-03-02 15:24:39 +0100 (So, 02 Mrz 2008) $
	$Revision:1236 $
	$URL:svn+ssh://zmag.de/home/timo/svn/diplomarbeit/code/one-way-editing/trunk/xsl/syncronize.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="no" encoding="UTF-8" />

	<!-- inclusions -->
	<xsl:include href="overwrite_simple_pageobjects.xsl" />
	<xsl:include href="overwrite_complex_pageobjects.xsl" />

	<!-- make the scribus and docbook document available -->
	<xsl:variable name="scribus" select="/" />
	<xsl:variable name="docbook" select="document($content)" />

	<!-- start with the scribus document root -->
	<xsl:template match="/">
		<!-- test if the $content parameter is passed -->
		<xsl:choose>
			<xsl:when test="$docbook/PAGEOBJECTS">
				<xsl:apply-templates />
			</xsl:when>
			<xsl:otherwise>
				<xsl:message>ERROR: INPUT ('<xsl:value-of select="$docbook"/>') is not valid</xsl:message>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<!-- copy all nodes and attributes of the scribus document -->
	<xsl:template match="@*|*">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<!-- detect if pageobject is simple or complex -->
	<xsl:template match="PAGEOBJECT">
		<xsl:choose>
			<!-- PAGEOBJECT has only one ITEXT node -->
			<xsl:when test="count(child::ITEXT)=1">
				<xsl:apply-templates select="." mode="simplePageobject" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates select="." mode="complexPageobject" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>