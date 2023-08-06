<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to overwrite the content of a complex pageobject.
	This stylesheet is part of the syncronize stylesheet.

	$Date: 2008-03-14 17:17:20 +0100 (Fri, 14 Mar 2008) $
	$Revision: 272 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/overwrite_complex_pageobjects.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- copy all attributes and overwrite all childnodes -->
	<xsl:template match="PAGEOBJECT" mode="complexPageobject">
		<xsl:message>-------------------------------------------------------</xsl:message>
		<xsl:message>complexPageobject (<xsl:value-of select="@ANNAME" />)</xsl:message>
		<xsl:copy>
			<xsl:variable name="anname" select="@ANNAME" />
			<!-- copy all attributes -->
			<xsl:apply-templates select="@*" />
			<!-- take only the para and bridgehead subnodes of the
			     corresponding article node -->
			<xsl:apply-templates
				select="$docbook//section[@id=$anname]/*"
				mode="complex-pageobject" />
		</xsl:copy>
	</xsl:template>

	<xsl:template match="para" mode="complex-pageobject">

		<!-- create ITEXT node -->
		<xsl:element name="ITEXT">
			<xsl:attribute name="CH">
			<xsl:value-of select="." />
			</xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<xsl:message>  +-ITEXT node created (<xsl:value-of select="." />)</xsl:message>
		</xsl:element>

		<!-- create para node -->
		<!-- <para PSHORTCUT="" SHORTCUT="" CNAME="" NAME="" /> -->
		<xsl:element name="para">
			<xsl:attribute name="PSHORTCUT"></xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<!-- <xsl:attribute name="PARENT">Default Paragraph Style</xsl:attribute> -->
			<xsl:message>  +-para node created</xsl:message>
		</xsl:element>

	</xsl:template>

	<xsl:template match="bridgehead" mode="complex-pageobject">

		<!-- create ITEXT node -->
		<xsl:element name="ITEXT">
			<xsl:attribute name="CH">
				<xsl:value-of select="." />
			</xsl:attribute>
			<xsl:message>  +-ITEXT node created (<xsl:value-of select="." />)</xsl:message>
		</xsl:element>

		<!-- create para node -->
		<!-- <para PSHORTCUT="" SHORTCUT="" CNAME="" NAME="" /> -->
		<xsl:element name="para">
			<xsl:attribute name="PSHORTCUT"></xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<!-- <xsl:attribute name="PARENT">Default Paragraph Style</xsl:attribute> -->
			<xsl:message>  +-para node created</xsl:message>
		</xsl:element>

</xsl:template>

</xsl:stylesheet>