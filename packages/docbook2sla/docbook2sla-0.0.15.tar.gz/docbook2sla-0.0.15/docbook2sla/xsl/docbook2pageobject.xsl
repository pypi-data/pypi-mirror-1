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

	<!-- attribute set for objects -->
	<xsl:attribute-set name="pageobject">
		<xsl:attribute name="OnMasterPage"></xsl:attribute>
		<xsl:attribute name="isGroupControl">0</xsl:attribute>
		<xsl:attribute name="BottomLine">0</xsl:attribute>
		<xsl:attribute name="REXTRA">0</xsl:attribute>
		<xsl:attribute name="gHeight">3.22151e-264</xsl:attribute>
		<xsl:attribute name="gWidth">3.22102e-264</xsl:attribute>
		<xsl:attribute name="NUMPO">16</xsl:attribute>
		<xsl:attribute name="TransBlendS">0</xsl:attribute>
		<xsl:attribute name="PLINEART">1</xsl:attribute>
		<xsl:attribute name="doOverprint">0</xsl:attribute>
		<xsl:attribute name="RightLine">0</xsl:attribute>
		<xsl:attribute name="LOCALSCX">1</xsl:attribute>
		<xsl:attribute name="ROT">0</xsl:attribute>
		<xsl:attribute name="ImageRes">1</xsl:attribute>
		<xsl:attribute name="GROUPS"></xsl:attribute>
		<xsl:attribute name="LOCKR">0</xsl:attribute>
		<xsl:attribute name="LOCALSCY">1</xsl:attribute>
		<xsl:attribute name="NAMEDLST"></xsl:attribute>
		<xsl:attribute name="isInline">0</xsl:attribute>
		<xsl:attribute name="AUTOTEXT">0</xsl:attribute>
		<xsl:attribute name="FLIPPEDV">0</xsl:attribute>
		<xsl:attribute name="PCOLOR">None</xsl:attribute>
		<xsl:attribute name="RADRECT">0</xsl:attribute>
		<xsl:attribute name="REVERS">0</xsl:attribute>
		<xsl:attribute name="PRINTABLE">1</xsl:attribute>
		<xsl:attribute name="RATIO">1</xsl:attribute>
		<xsl:attribute name="FLIPPEDH">0</xsl:attribute>
		<xsl:attribute name="COLGAP">0</xsl:attribute>
		<xsl:attribute name="PCOLOR2">None</xsl:attribute>
		<xsl:attribute name="NEXTITEM">-1</xsl:attribute>
		<xsl:attribute name="NUMGROUP">0</xsl:attribute>
		<xsl:attribute name="TransValue">0</xsl:attribute>
		<xsl:attribute name="textPathFlipped">0</xsl:attribute>
		<xsl:attribute name="PLINEEND">0</xsl:attribute>
		<xsl:attribute name="FRTYPE">0</xsl:attribute>
		<xsl:attribute name="PTYPE">4</xsl:attribute>
		<xsl:attribute name="ImageClip"></xsl:attribute>
		<xsl:attribute name="isTableItem">0</xsl:attribute>
		<xsl:attribute name="TEXTFLOW2">0</xsl:attribute>
		<xsl:attribute name="SHADE2">100</xsl:attribute>
		<xsl:attribute name="PWIDTH">1</xsl:attribute>
		<xsl:attribute name="DASHOFF">0</xsl:attribute>
		<xsl:attribute name="PFILE2"></xsl:attribute>
		<xsl:attribute name="PFILE"></xsl:attribute>
		<xsl:attribute name="TEXTFLOW3">0</xsl:attribute>
		<xsl:attribute name="textPathType">0</xsl:attribute>
		<xsl:attribute name="PLTSHOW">0</xsl:attribute>
		<xsl:attribute name="CLIPEDIT">0</xsl:attribute>
		<xsl:attribute name="BACKITEM">-1</xsl:attribute>
		<xsl:attribute name="TransValueS">0</xsl:attribute>
		<xsl:attribute name="EMBEDDED">1</xsl:attribute>
		<xsl:attribute name="PFILE3"></xsl:attribute>
		<xsl:attribute name="SHADE">100</xsl:attribute>
		<xsl:attribute name="fillRule">1</xsl:attribute>
		<xsl:attribute name="COCOOR">0 0 0 0 259 0 259 0 259 0 259 0 259 190 259 190 259 190 259 190 0 190 0 190 0 190 0 190 0 0 0 0 </xsl:attribute>
		<xsl:attribute name="BASEOF">0</xsl:attribute>
		<xsl:attribute name="PICART">1</xsl:attribute>
		<xsl:attribute name="COLUMNS">1</xsl:attribute>
		<xsl:attribute name="OwnPage">0</xsl:attribute>
		<xsl:attribute name="LAYER">0</xsl:attribute>
		<xsl:attribute name="BOOKMARK">0</xsl:attribute>
		<xsl:attribute name="gYpos">3.22054e-264</xsl:attribute>
		<xsl:attribute name="startArrowIndex">0</xsl:attribute>
		<xsl:attribute name="TopLine">0</xsl:attribute>
		<xsl:attribute name="LOCK">0</xsl:attribute>
		<xsl:attribute name="EPROF"></xsl:attribute>
		<xsl:attribute name="gXpos">3.22005e-264</xsl:attribute>
		<xsl:attribute name="DASHS"></xsl:attribute>
		<xsl:attribute name="IRENDER">1</xsl:attribute>
		<xsl:attribute name="TEXTFLOW">0</xsl:attribute>
		<xsl:attribute name="TEXTFLOWMODE">0</xsl:attribute>
		<xsl:attribute name="ANNOTATION">0</xsl:attribute>
		<xsl:attribute name="LOCALX">0</xsl:attribute>
		<xsl:attribute name="GRTYP">0</xsl:attribute>
		<xsl:attribute name="NUMCO">16</xsl:attribute>
		<xsl:attribute name="EXTRA">0</xsl:attribute>
		<xsl:attribute name="LOCALY">0</xsl:attribute>
		<xsl:attribute name="NUMDASH">0</xsl:attribute>
		<xsl:attribute name="LeftLine">0</xsl:attribute>
		<xsl:attribute name="PRFILE"></xsl:attribute>
		<xsl:attribute name="TEXTRA">0</xsl:attribute>
		<xsl:attribute name="SCALETYPE">1</xsl:attribute>
		<xsl:attribute name="endArrowIndex">0</xsl:attribute>
		<xsl:attribute name="TransBlend">0</xsl:attribute>
		<xsl:attribute name="BEXTRA">0</xsl:attribute>
		<xsl:attribute name="PLINEJOIN">0</xsl:attribute>
	</xsl:attribute-set>

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