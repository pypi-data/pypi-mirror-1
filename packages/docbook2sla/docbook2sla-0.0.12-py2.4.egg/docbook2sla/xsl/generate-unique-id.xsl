<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to create unique ids for every xml node.

	$Date: 2008-03-03 12:26:29 +0100 (Mon, 03 Mar 2008) $
	$Revision: 192 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/generate-id.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:key name="ids" match="//*" use="@id" />

	<xsl:template match="*">
		<xsl:copy>
			<xsl:if test="not(@id)">
				<xsl:attribute name="id">
					<xsl:call-template name="generate-unique-id">
						<xsl:with-param name="prefix"
							select="generate-id()" />
					</xsl:call-template>
				</xsl:attribute>
			</xsl:if>
			<xsl:apply-templates select="*|@*|text()" />
		</xsl:copy>
	</xsl:template>

	<xsl:template name="generate-unique-id">
		<xsl:param name="prefix" />
		<xsl:param name="suffix"></xsl:param>
		<xsl:variable name="id" select="concat($prefix,$suffix)" />

		<xsl:choose>
			<xsl:when test="key('ids',$id)">
				<xsl:call-template name="generate-unique-id">
					<xsl:with-param name="prefix" select="$prefix" />
					<xsl:with-param name="suffix"
						select="concat($suffix,'x')" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$id" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="@*|text()">
		<xsl:copy />
	</xsl:template>

</xsl:stylesheet>