<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- ################################################################################################### -->
  <!-- ATTRIBUTE-SETS                                                                                      -->
  <!-- ################################################################################################### -->

  <!-- GLOBAL STYLES -->
  <!-- As ordered as in the Scribus UI. Almost done. -->
  <xsl:attribute-set name="STYLE-Node">
    <!-- NAME -->
    <xsl:attribute name="NAME"/> 		<!-- style name -->
    <!-- ATTRIBUTES: MARGINS AND ALIGNMENT -->
    <xsl:attribute name="LINESP"/>		<!-- line spacing -->
    <xsl:attribute name="VOR"/> 		<!-- gap before -->
    <xsl:attribute name="NACH"/> 		<!-- gap after -->
    <xsl:attribute name="ALIGN"/> 		<!-- alignment -->
    <!-- ATTRIBUTES: DROP CAP -->
    <xsl:attribute name="DROP"/>		<!-- drop Cap: 1|0 -->
    <xsl:attribute name="DROPLIN"/> 	<!-- drop cap lines -->
    <xsl:attribute name="DROPDIST"/>	<!-- drop cap distance from text -->
    <!-- ATTRIBUTES: TABS AND INDENTS -->
    <xsl:attribute name="RMARGIN"/> 	<!-- right margin -->
    <xsl:attribute name="LINESPMode"/> 	<!-- line spacing Mode -->
    <xsl:attribute name="FIRST"/> 		<!-- first indent -->
    <xsl:attribute name="INDENT"/> 		<!-- indent / left margin -->
    <xsl:attribute name="FONTSIZE"/>	<!-- font -->
    <xsl:attribute name="FONT"/>		<!-- font size -->
	<!-- CHARACTER STYLE -->
    <xsl:attribute name="CNAME"/>		<!-- ??? -->
	<!-- SHORTCUTS -->
    <xsl:attribute name="SHORTCUT"/>	<!-- shortcut -->
    <xsl:attribute name="PSHORTCUT"/>	<!-- ??? -->
  </xsl:attribute-set>

  <!-- CHARACTER STYLES -->
  <!-- As ordered as in the Scribus UI. Much to do. -->
  <xsl:attribute-set name="CHARSTYLE-Node">
    <!-- NAME -->
    <xsl:attribute name="CNAME"/>		<!-- character style name -->
    <!-- BASED ON -->
	<xsl:attribute name="CPARENT"/> 	<!-- character style parent (based on???) -->
	<!-- ATTRIBUTES: Grundlegende Formatierung -->
	<!-- ATTRIBUTES: Erweiterte Formatierung -->
	<xsl:attribute name="FONT"/> 		<!-- font -->
	<xsl:attribute name="FONTSIZE"/> 	<!-- fontsize -->
	<xsl:attribute name="FEATURES"/> 	<!-- features -->
	<xsl:attribute name="FCOLOR"/> 		<!-- fill color -->
	<xsl:attribute name="FSHADE"/> 		<!-- fill shade -->
	<xsl:attribute name="SSHADE"/> 		<!-- stroke shade -->
	<xsl:attribute name="TXTSHX"/> 		<!-- shadow XOffset -->
	<xsl:attribute name="TXTSHY"/> 		<!-- shadow YOffset -->
	<xsl:attribute name="TXTOUT"/> 		<!-- outline width -->
	<xsl:attribute name="TXTULP"/> 		<!-- underline offset -->
	<xsl:attribute name="TXTULW"/> 		<!-- underline width -->
	<xsl:attribute name="TXTSTP"/> 		<!-- strikethru Offset -->
	<xsl:attribute name="TXTSTW"/> 		<!-- strikethru Width -->
	<xsl:attribute name="SCALEH"/> 		<!-- scaleH -->
	<xsl:attribute name="SCALEV"/> 		<!-- scaleV -->
	<xsl:attribute name="BASEO"/> 		<!-- baseline offset -->
	<xsl:attribute name="KERN"/> 		<!-- tracking -->
	<xsl:attribute name="wordTrack"/> 	<!-- word Tracking -->
	<!-- ATTRIBUTES: Colors -->
	<xsl:attribute name="SCOLOR"/> 		<!-- stroke color -->
	<!-- SHORTCUTS -->
	<xsl:attribute name="SHORTCUT"/> 	<!-- shortcut -->
  </xsl:attribute-set>

  <!-- PAGEOBJECT -->
  <xsl:attribute-set name="PAGEOBJECT-Node">
    <!-- XYZ -->
    <xsl:attribute name="OnMasterPage"/>
    <xsl:attribute name="isGroupControl">0</xsl:attribute>
    <xsl:attribute name="BottomLine">0</xsl:attribute>
    <xsl:attribute name="REXTRA">0</xsl:attribute>
    <xsl:attribute name="gHeight">3.08737e-264</xsl:attribute>
    <xsl:attribute name="gWidth">3.08688e-264</xsl:attribute>
    <xsl:attribute name="NUMPO">16</xsl:attribute>
    <xsl:attribute name="TransBlendS">0</xsl:attribute>
    <xsl:attribute name="PLINEART">1</xsl:attribute>
    <xsl:attribute name="doOverprint">0</xsl:attribute>
    <xsl:attribute name="RightLine">0</xsl:attribute>
    <xsl:attribute name="LOCALSCX">1</xsl:attribute>
    <xsl:attribute name="ROT">0</xsl:attribute>
    <xsl:attribute name="WIDTH">335</xsl:attribute>
    <xsl:attribute name="ImageRes">1</xsl:attribute>
    <xsl:attribute name="GROUPS"/>
    <xsl:attribute name="LOCKR">0</xsl:attribute>
    <xsl:attribute name="LOCALSCY">1</xsl:attribute>
    <xsl:attribute name="NAMEDLST"/>
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
    <xsl:attribute name="ImageClip"/>
    <xsl:attribute name="isTableItem">0</xsl:attribute>
    <xsl:attribute name="TEXTFLOW2">0</xsl:attribute>
    <xsl:attribute name="SHADE2">100</xsl:attribute>
    <xsl:attribute name="PWIDTH">1</xsl:attribute>
    <xsl:attribute name="HEIGHT">219</xsl:attribute>
    <xsl:attribute name="DASHOFF">0</xsl:attribute>
    <xsl:attribute name="PFILE2"/>
    <xsl:attribute name="PFILE"/>
    <xsl:attribute name="TEXTFLOW3">0</xsl:attribute>
    <xsl:attribute name="textPathType">0</xsl:attribute>
    <xsl:attribute name="PLTSHOW">0</xsl:attribute>
    <xsl:attribute name="CLIPEDIT">0</xsl:attribute>
    <xsl:attribute name="BACKITEM">-1</xsl:attribute>
    <xsl:attribute name="TransValueS">0</xsl:attribute>
    <xsl:attribute name="EMBEDDED">1</xsl:attribute>
    <xsl:attribute name="PFILE3"/>
    <xsl:attribute name="ANNAME"/>
    <xsl:attribute name="SHADE">100</xsl:attribute>
    <xsl:attribute name="fillRule">1</xsl:attribute>
    <xsl:attribute name="COCOOR">0 0 0 0 335 0 335 0 335 0 335 0 335 219 335 219 335 219 335 219 0 219 0 219 0 219 0 219 0 0 0 0</xsl:attribute>
    <xsl:attribute name="BASEOF">0</xsl:attribute>
    <xsl:attribute name="PICART">1</xsl:attribute>
    <xsl:attribute name="COLUMNS">1</xsl:attribute>
    <xsl:attribute name="OwnPage">0</xsl:attribute>
    <xsl:attribute name="LAYER">0</xsl:attribute>
    <xsl:attribute name="BOOKMARK">0</xsl:attribute>
    <xsl:attribute name="gYpos">3.0864e-264</xsl:attribute>
    <xsl:attribute name="startArrowIndex">0</xsl:attribute>
    <xsl:attribute name="TopLine">0</xsl:attribute>
    <xsl:attribute name="LOCK">0</xsl:attribute>
    <xsl:attribute name="EPROF"></xsl:attribute>
    <xsl:attribute name="gXpos">3.08592e-264</xsl:attribute>
    <xsl:attribute name="DASHS"></xsl:attribute>
    <xsl:attribute name="IRENDER">1</xsl:attribute>
    <xsl:attribute name="TEXTFLOW">0</xsl:attribute>
    <xsl:attribute name="YPOS">96</xsl:attribute>
    <xsl:attribute name="TEXTFLOWMODE">0</xsl:attribute>
    <xsl:attribute name="ANNOTATION">0</xsl:attribute>
    <xsl:attribute name="LOCALX">0</xsl:attribute>
    <xsl:attribute name="GRTYP">0</xsl:attribute>
    <xsl:attribute name="XPOS">206</xsl:attribute>
    <xsl:attribute name="NUMCO">16</xsl:attribute>
    <xsl:attribute name="POCOOR">0 0 0 0 335 0 335 0 335 0 335 0 335 219 335 219 335 219 335 219 0 219 0 219 0 219 0 219 0 0 0 0</xsl:attribute>
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

    <!-- XYZ -->

    <!-- FORM -->

    <!-- GROUP -->

    <!-- TEXT -->

    <!-- IMAGE -->

    <!-- LINES -->

    <!-- COLORS -->

  </xsl:attribute-set>

  <!-- ITEXT -->
  <xsl:attribute-set name="ITEXT-Node">
    <xsl:attribute name="CH"></xsl:attribute>
    <xsl:attribute name="SHORTCUT"></xsl:attribute>
    <xsl:attribute name="CNAME"></xsl:attribute>
    <xsl:attribute name="FONTSIZE"></xsl:attribute>
    <xsl:attribute name="FONT"></xsl:attribute>
  </xsl:attribute-set>

  <!-- para -->
  <xsl:attribute-set name="PARA-Node">
    <xsl:attribute name="PSHORTCUT"></xsl:attribute>
    <xsl:attribute name="SHORTCUT"></xsl:attribute>
    <xsl:attribute name="CNAME"></xsl:attribute>
    <xsl:attribute name="NAME"></xsl:attribute>
  </xsl:attribute-set>

</xsl:stylesheet>