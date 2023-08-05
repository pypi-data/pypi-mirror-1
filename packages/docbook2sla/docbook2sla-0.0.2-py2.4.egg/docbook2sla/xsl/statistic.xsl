<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="yes" encoding="UTF-8" />

	<xsl:template match="/">
		<xsl:variable name="PAGEOBJECTS" select="/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT" />
		<xsl:message>===========</xsl:message>
		<xsl:message>STATISTICS:</xsl:message>
		<xsl:message>===========</xsl:message>
		<xsl:message>PAGEOBJECTS: <xsl:value-of select="count($PAGEOBJECTS)"/></xsl:message>
		<xsl:apply-templates select="/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT" />
	</xsl:template>

	<xsl:template match="PAGEOBJECT">
		<xsl:choose>
			<xsl:when test="@PFILE != ''">
				<xsl:message>BILD : '<xsl:value-of select="@ANNAME" />'</xsl:message>
			</xsl:when>
			<xsl:otherwise>
				<xsl:message>TEXT : '<xsl:value-of select="@ANNAME" />'</xsl:message>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>
