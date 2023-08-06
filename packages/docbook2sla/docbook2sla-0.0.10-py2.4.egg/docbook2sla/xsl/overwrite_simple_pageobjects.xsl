<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to overwrite a simple pageobject.

	$Date: 2008-03-03 12:26:29 +0100 (Mon, 03 Mar 2008) $
	$Revision: 192 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/overwrite_simple_pageobjects.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- copy all attributes and childnodes and overwrite the ITEXT node -->
	<xsl:template match="PAGEOBJECT" mode="simplePageobject">
		<xsl:copy>
			<!-- copy all attributes -->
			<xsl:apply-templates select="@*" />
			<!-- overwrite ITEXT node -->
			<xsl:apply-templates select="child::ITEXT"
				mode="overwrite-ch">
				<xsl:with-param name="pageobject-name">
					<xsl:value-of select="@ANNAME" />
				</xsl:with-param>
			</xsl:apply-templates>
			<!-- copy para node -->
			<xsl:apply-templates select="child::para|child::PageItemAttributes" />
		</xsl:copy>
	</xsl:template>

	<!-- overwrite the CH attribute of the ITEXT node -->
	<xsl:template match="*" mode="overwrite-ch">
		<xsl:param name="pageobject-name" />
		<xsl:message>+- overwrite CH attribute</xsl:message>
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
			<xsl:attribute name="CH">
				<xsl:apply-templates
					select="$docbook/book/article/*[name()=$pageobject-name]" />
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

	<!-- copy every page object, and overwrite the content -->
	<xsl:template match="APAGEOBJECT">
		<!-- copy the attributes of the PAGEOBEJCT node -->
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
		<xsl:param name="anname" select="@ANNAME" />
		<!-- find the right docbook node -->
		<xsl:param name="docbookid" select="$docbook//*[@id=$anname]" />
		<FOO><xsl:value-of select="$docbookid"></xsl:value-of></FOO>

	</xsl:template>

	<xsl:template match="dsf">
		<xsl:copy>
			<!-- copy every attribute and childnode of PAGEOBJECT -->
			<xsl:apply-templates select="@*|node()" />
			<!-- overwrite the CH attribute of the ITEXT -->
			<xsl:attribute name="CH">
				<!-- find docbook (@id) node with the id of the pageobject (@ANNAME) -->
				<xsl:apply-templates select="$docbook//*[@id=$anname]" />
			</xsl:attribute>
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>