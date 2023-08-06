<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to create scribus pageobjects from docbook source.

	Input:		valid Scribus document
	Output:		Scribus pageobjects

	Usage: 	xsltproc \
				- -noout \
				docbook2pageobject.xsl \
				../tests/data/xml/article+id.xml

	$Date: 2008-03-14 17:39:46 +0100 (Fri, 14 Mar 2008) $
	$Revision: 274 $
	$URL: http://svn.zmag.de/svn/python/docbook2sla/trunk/docbook2sla/xsl/docbook2pageobject.xsl $

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- xml declaration -->
	<xsl:output omit-xml-declaration="yes" encoding="UTF-8" indent="yes" />

	<!-- inclusions -->
	<xsl:include href="create_pageobject.xsl" />

	<xsl:template match="/">
		<PAGEOBJECTS>
			<xsl:message><xsl:text> </xsl:text></xsl:message>
			<xsl:message>=======================================================</xsl:message>
			<xsl:message>DocBook To Scribus Pageobjects Transformation          </xsl:message>
			<xsl:message>=======================================================</xsl:message>
			<xsl:message><xsl:text> </xsl:text></xsl:message>
			<xsl:message>-------------------------------------------------------</xsl:message>
			<xsl:message>PAGEOBJECTS node created</xsl:message>
			<xsl:apply-templates />
			<xsl:message>-------------------------------------------------------</xsl:message>
			<xsl:message><xsl:text> </xsl:text></xsl:message>
		</PAGEOBJECTS>
	</xsl:template>

	<!-- complex pageobjects -->
	<xsl:template match="article/section">
		<xsl:call-template name="createPageObject">
			<xsl:with-param name="simple">0</xsl:with-param>
			<xsl:with-param name="id" select="@id" />
		</xsl:call-template>
	</xsl:template>

	<!-- simple pageobjects -->
	<xsl:template match=" title | subtitle | blockquote | pubdate ">
		<xsl:call-template name="createPageObject">
			<xsl:with-param name="simple">1</xsl:with-param>
			<xsl:with-param name="id" select="@id" />
		</xsl:call-template>
	</xsl:template>

	<!-- image pageobject -->
	<xsl:template match="mediaobject">
		<xsl:call-template name="createImagePageObject">
			<xsl:with-param name="type">image</xsl:with-param>
			<xsl:with-param name="id" select="@id" />
			<xsl:with-param name="width">300</xsl:with-param>
			<xsl:with-param name="height">300</xsl:with-param>
			<xsl:with-param name="xpos">180</xsl:with-param>
			<xsl:with-param name="ypos">80</xsl:with-param>
			<xsl:with-param name="src" select="imageobject/imagedata/@fileref" />
			<xsl:with-param name="caption" select="caption/para" />
		</xsl:call-template>
	</xsl:template>

	<xsl:template name="createPageObject">
		<xsl:param name="simple" />
		<xsl:param name="id" />
		<xsl:message>-------------------------------------------------------</xsl:message>
		<xsl:message>PAGEOBJECT node created (<xsl:value-of select="$id" />)</xsl:message>
  		<xsl:element name="PAGEOBJECT" xsl:use-attribute-sets="pageobject" >
			<xsl:if test="$simple=1">
				<xsl:attribute name="ANNAME"><xsl:value-of select="$id" /></xsl:attribute>
				<xsl:attribute name="WIDTH">259</xsl:attribute>
				<xsl:attribute name="HEIGHT">80</xsl:attribute>
				<xsl:attribute name="XPOS">180</xsl:attribute>
				<xsl:attribute name="YPOS">80</xsl:attribute>
				<xsl:attribute name="POCOOR">0 0 0 0 259 0 259 0 259 0 259 0 259 80 259 80 259 80 259 80 0 80 0 80 0 80 0 80 0 0 0 0 </xsl:attribute>
	  			<xsl:call-template name="createSimplePageObjectContent" />
	  		</xsl:if>
	  		<xsl:if test="$simple=0">
				<xsl:attribute name="ANNAME"><xsl:value-of select="$id" /></xsl:attribute>
				<xsl:attribute name="WIDTH">259</xsl:attribute>
				<xsl:attribute name="HEIGHT">190</xsl:attribute>
				<xsl:attribute name="XPOS">180</xsl:attribute>
				<xsl:attribute name="YPOS">180</xsl:attribute>
				<xsl:attribute name="POCOOR">0 0 0 0 259 0 259 0 259 0 259 0 259 190 259 190 259 190 259 190 0 190 0 190 0 190 0 190 0 0 0 0 </xsl:attribute>
	  			<xsl:call-template name="createComplexPageObjectContent" />
	  		</xsl:if>
			<PageItemAttributes/>
  		</xsl:element>
	</xsl:template>

	<xsl:template name="createSimplePageObjectContent">

		<!-- create ITEXT node -->
		<!-- <ITEXT CH="" SHORTNAME="" CNAME="" /> -->
		<xsl:element name="ITEXT">
			<xsl:attribute name="CH">
				<xsl:value-of select="." />
			</xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
		</xsl:element>
		<xsl:message> +- ITEXT (<xsl:value-of select="." />)</xsl:message>

		<!-- create para node -->
		<!-- <para PSHORTCUT="" SHORTCUT="" CNAME="" NAME="" /> -->
		<xsl:element name="para">
			<xsl:attribute name="PSHORTCUT"></xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<!-- <xsl:attribute name="PARENT">Standard-Absatzstil</xsl:attribute> -->
		</xsl:element>
		<xsl:message> +- para</xsl:message>

	</xsl:template>

	<xsl:template name="createComplexPageObjectContent">
		<xsl:if test="para|bridgehead">
			<xsl:apply-templates select=" para | bridgehead " />
		</xsl:if>
	</xsl:template>

	<!-- para -->
	<xsl:template match=" para | bridgehead ">

		<!-- create ITEXT node -->
		<!-- <ITEXT CH="" SHORTNAME="" CNAME="" /> -->
		<xsl:element name="ITEXT">
			<xsl:attribute name="CH">
				<xsl:value-of select="." />
			</xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
		</xsl:element>
		<xsl:message> +- ITEXT (<xsl:value-of select="." />)</xsl:message>

		<!-- create para node -->
		<!-- <para PSHORTCUT="" SHORTCUT="" CNAME="" NAME="" /> -->
		<xsl:element name="para">
			<xsl:attribute name="PSHORTCUT"></xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<!-- <xsl:attribute name="PARENT">Standard-Absatzstil</xsl:attribute> -->
		</xsl:element>
		<xsl:message> +- para</xsl:message>

	</xsl:template>

</xsl:stylesheet>