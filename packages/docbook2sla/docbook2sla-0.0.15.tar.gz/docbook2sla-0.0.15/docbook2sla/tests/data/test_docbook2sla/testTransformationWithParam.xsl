<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to test the transform function of DocBook2Sla.

	$Date:$
	$Revision:$
	$URL:$

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="yes" />

	<xsl:variable name="mydoc" select="document($secondinput)" />

	<xsl:template match="/">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="foo">
		<fromExternal>
			<xsl:value-of select="$mydoc/*" />
		</fromExternal>
	</xsl:template>

</xsl:stylesheet>