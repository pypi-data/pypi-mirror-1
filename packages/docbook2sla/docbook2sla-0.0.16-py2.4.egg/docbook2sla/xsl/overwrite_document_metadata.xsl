<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to overwrite the metadata attributes of the document node.
	This stylesheet is part of the syncronize stylesheet.

	$Date$
	$Revision$
	$URL$

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="DOCUMENT">
		<xsl:copy>
			<!-- copy all attributes -->
			<xsl:apply-templates select="@*" />

			<!-- Date related to life-cycle of the document, YYYY-MM-DD -->
			<xsl:attribute name="DOCDATE"/>
			<!-- Person or organization making contributions to the document -->
			<xsl:attribute name="DOCCONTRIB" />
			<!-- Reference to a document from which this document is derived -->
			<xsl:attribute name="DOCSOURCE">foo</xsl:attribute>

			<!-- copy all subnodes -->
			<xsl:apply-templates select="node()" />
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>