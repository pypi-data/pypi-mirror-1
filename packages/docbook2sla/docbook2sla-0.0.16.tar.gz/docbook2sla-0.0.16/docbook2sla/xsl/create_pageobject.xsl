<?xml version="1.0" encoding="utf-8"?>

<!--
	========================================================================

	Stylesheet to create a scribus pageobject

	createPageObject(type, id, width, height, xpos, ypos)
	createITEXT(text)
	createPara()

	$Date$
	$Revision$
	$URL$

	Timo Stollenwerk | timo@zmag.de

    ========================================================================
-->

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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

	<xsl:template name="createImagePageObject">

		<!-- parameters -->
		<xsl:param name="type" />
		<xsl:param name="id" />
		<xsl:param name="width" />
		<xsl:param name="height" />
		<xsl:param name="xpos" />
		<xsl:param name="ypos" />
		<!-- text page objects -->
		<xsl:param name="text" />
		<!-- image page objects -->
		<xsl:param name="src" />
		<xsl:param name="caption" />

		<!-- Coordinates of the object shape -->
		<xsl:variable name="POCOOR">0 0 0 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 0 0 0</xsl:variable>

		<!-- Coordinates of the objects contour line -->
		<xsl:variable name="COCOOR">0 0 0 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> 0 <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> <xsl:text> </xsl:text> <xsl:value-of select="$width" /> <xsl:text> </xsl:text> <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 <xsl:value-of select="$height" /> 0 0 0 0</xsl:variable>


		<!-- output message -->
		<xsl:message>-------------------------------------------------------</xsl:message>
		<xsl:message>PAGEOBJECT node created (<xsl:value-of select="$id" />)</xsl:message>
		<!-- create PAGEOBJECT element -->
  		<xsl:element name="PAGEOBJECT" xsl:use-attribute-sets="pageobject">
			<xsl:attribute name="ANNAME"><xsl:value-of select="$id" /></xsl:attribute>
			<xsl:attribute name="WIDTH"><xsl:value-of select="$width" /></xsl:attribute>
			<xsl:attribute name="HEIGHT"><xsl:value-of select="$height" /></xsl:attribute>
			<xsl:attribute name="XPOS"><xsl:value-of select="$xpos" /></xsl:attribute>
			<xsl:attribute name="YPOS"><xsl:value-of select="$ypos" /></xsl:attribute>
			<xsl:attribute name="POCOOR"><xsl:value-of select="$POCOOR" /></xsl:attribute>
			<xsl:attribute name="COCOOR"><xsl:value-of select="$COCOOR" /></xsl:attribute>

			<!-- image -->
			<xsl:if test="$type='image'">
				<!-- set frame type to image -->
				<xsl:attribute name="PTYPE">2</xsl:attribute>
				<xsl:attribute name="EMBEDDED">0</xsl:attribute>
				<xsl:attribute name="IRENDER">0</xsl:attribute>
				<xsl:attribute name="PFILE"><xsl:value-of select="$src" /></xsl:attribute>
				<xsl:message> +- @PFILE (<xsl:value-of select="$src" />)</xsl:message>
				<para
					PSHORTCUT=""
					SHORTCUT=""
					CNAME=""
					NAME="" />
	  		</xsl:if>

	  		<!-- simple text page object -->
	  		<xsl:if test="$type='simpletext'">
  				<!-- simple page object -->
				<xsl:call-template name="createITEXT">
					<xsl:with-param name="text" select="$text" />
				</xsl:call-template>
				<xsl:call-template name="createPara" />
	  		</xsl:if>

	  		<!-- complex text page object -->
	  		<xsl:if test="$type='complextext'">
	  			<xsl:message>complex text</xsl:message>
	  			<xsl:message><xsl:value-of select="name()" /></xsl:message>
				<xsl:for-each select="child::*">
					<xsl:call-template name="createITEXT">
						<xsl:with-param name="text">
							<xsl:value-of select="."/>
						</xsl:with-param>
					</xsl:call-template>
					<xsl:call-template name="createPara" />
				</xsl:for-each>
	  		</xsl:if>

			<xsl:message> +- PageItemAttributes</xsl:message>
			<PageItemAttributes />
  		</xsl:element>
	</xsl:template>

	<!-- ITEXT node -->
	<xsl:template name="createITEXT">
		<xsl:param name="text" />
		<xsl:element name="ITEXT">
			<xsl:attribute name="CH">
				<xsl:value-of select="$text" />
			</xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
		</xsl:element>
		<xsl:message> +- ITEXT (<xsl:value-of select="$text" />)</xsl:message>
	</xsl:template>

	<!-- para node -->
	<xsl:template name="createPara">
		<xsl:element name="para">
			<xsl:attribute name="PSHORTCUT"></xsl:attribute>
			<xsl:attribute name="SHORTCUT"></xsl:attribute>
			<xsl:attribute name="CNAME"></xsl:attribute>
			<!-- <xsl:attribute name="PARENT">Standard-Absatzstil</xsl:attribute> -->
		</xsl:element>
		<xsl:message> +- para</xsl:message>
	</xsl:template>

</xsl:stylesheet>