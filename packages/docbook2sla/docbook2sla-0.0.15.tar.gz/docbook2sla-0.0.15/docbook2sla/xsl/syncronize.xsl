<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to syncronise the content of a DocBook file with an existing
	Scribus file.

	Scribus pageobjects with no corresponding docbook node are ignored.

	Input:		valid Scribus document
	Parameter:	valid DocBook document ($content)

	Usage: 	xsltproc \
				- -noout \
				- -stringparam secondinput ../tests/data/test_syncronize/docbook.xml \
				syncronize.xsl \
				../tests/data/test_syncronize/scribus.sla

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
	<xsl:variable name="docbook" select="document($secondinput)" />

	<!-- start with the scribus document root -->
	<xsl:template match="/">
		<xsl:choose>
			<xsl:when test="not(/SCRIBUSUTF8NEW)">
				<xsl:message>ERROR (syncronize.xsl): Input is no Scribus document</xsl:message>
			</xsl:when>
			<xsl:when test="not($docbook/book|$docbook/article)">
				<xsl:message>ERROR (syncronize.xsl): Input ('<xsl:value-of select="$docbook"/>') is no DocBook document</xsl:message>
			</xsl:when>
			<xsl:otherwise>
				<xsl:message>-------------------------------------------------------</xsl:message>
				<xsl:message>Input validation passed</xsl:message>
				<xsl:apply-templates />
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
		<!-- test if there is a corresponding docbook node -->
		<xsl:choose>
			<!-- there is a corresponding docbook node: inject content from docbook -->
			<xsl:when test="$docbook//@id=@ANNAME">
				<xsl:choose>
					<!-- corresponding docbook node is a complex pageobject (section) -->
					<xsl:when test="$docbook//section/@id=@ANNAME">
						<xsl:apply-templates select="." mode="complexPageobject" />
					</xsl:when>
					<!-- all others docbook nodes are simple pageobjects -->
					<xsl:otherwise>
						<xsl:apply-templates select="." mode="simplePageobject" />
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<!-- there is no corresponding docbook node: copy the whole pageobject -->
			<xsl:otherwise>
				<xsl:message>-------------------------------------------------------</xsl:message>
				<xsl:message>ignore pageobject (<xsl:value-of select="@ANNAME" />)</xsl:message>
				<xsl:copy>
					<xsl:apply-templates select="@*|node()" />
				</xsl:copy>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>