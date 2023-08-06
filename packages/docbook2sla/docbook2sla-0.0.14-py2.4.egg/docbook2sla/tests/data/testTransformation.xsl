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

	<xsl:template match="/">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="foo">
		<bar>
			<xsl:apply-templates />
		</bar>
	</xsl:template>

	<xsl:template match="bar">
		<foo>
			<xsl:apply-templates />
		</foo>
	</xsl:template>

</xsl:stylesheet>