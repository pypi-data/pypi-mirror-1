<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to overwrite a simple pageobject.
	This stylesheet is part of the syncronize stylesheet.

	$Date: 2008-03-12 10:18:20 +0100 (Wed, 12 Mar 2008) $
	$Revision: 262 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/overwrite_simple_pageobjects.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- copy all attributes and childnodes and overwrite the ITEXT node -->
	<xsl:template match="PAGEOBJECT" mode="simplePageobject">
		<xsl:message>-------------------------------------------------------</xsl:message>
		<xsl:message>simplePageobject (<xsl:value-of select="@ANNAME" />)</xsl:message>
		<xsl:copy>
			<!-- copy all attributes -->
			<xsl:apply-templates select="@*" />
			<!-- overwrite ITEXT node -->
			<xsl:apply-templates select="child::ITEXT"
				mode="overwrite-ch">
				<xsl:with-param name="pageobject-id">
					<xsl:value-of select="@ANNAME" />
				</xsl:with-param>
			</xsl:apply-templates>
			<!-- copy para node -->
			<xsl:apply-templates select="child::para|child::PageItemAttributes" />
		</xsl:copy>
	</xsl:template>

	<!-- overwrite the CH attribute of the ITEXT node -->
	<xsl:template match="*" mode="overwrite-ch">
		<xsl:param name="pageobject-id" />
		<xsl:message>+- overwrite CH attribute (<xsl:value-of select="$docbook//*[@id=$pageobject-id]" />)</xsl:message>
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
			<xsl:attribute name="CH">
				<xsl:apply-templates
					select="$docbook//*[@id=$pageobject-id]" />
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>