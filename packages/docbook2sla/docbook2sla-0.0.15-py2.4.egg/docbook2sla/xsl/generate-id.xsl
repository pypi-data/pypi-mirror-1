<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to create unique ids for every xml node.

	$Date: 2008-03-07 15:19:59 +0100 (Fri, 07 Mar 2008) $
	$Revision: 235 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/generate-id.xsl $

	Timo Stollenwerk | timo@zmag.de

	========================================================================
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
     version="1.0">

	<xsl:output method="xml" omit-xml-declaration="yes"/>

	<xsl:template match="book | article | title | subtitle ">
   		<xsl:copy>

				<xsl:attribute name="id">
					<xsl:value-of select="generate-id(.)"/>
				</xsl:attribute>

			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>