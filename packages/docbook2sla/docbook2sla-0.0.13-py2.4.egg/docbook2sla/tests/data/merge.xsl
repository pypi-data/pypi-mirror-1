<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- ################################################################################################# -->
  <!-- ###                                                                                           ### -->
  <!-- ### This stylesheet merges a xml docbook file into a scribus sla template file.               ### -->
  <!-- ###                                                                                           ### -->
  <!-- ################################################################################################# -->

  <!-- includes -->
  <!-- <xsl:include href="merge_simple_pageobjects.xsl"/> -->
  <xsl:include href="merge_complex_pageobjects.xsl"/>
  <!-- <xsl:include href="merge_attribute-sets.xsl"/> -->

  <!-- xml declaration -->
  <xsl:output omit-xml-declaration="no" encoding="UTF-8" />

  <!-- make layout.sla available as well as content.xml -->
  <xsl:variable name="content" select="/" />
  <xsl:variable name="layout" select="document($uselayout)" />

  <!-- ################################################################################################# -->
  <!-- ### START WITH THE SCRIBUS LAYOUT TEMPLATE AND COPY ALL NODES AND ATTRIBUTES                  ### -->
  <!-- ################################################################################################# -->

  <!-- start -->
  <xsl:template match="/">

    <!-- message output -->
    <xsl:message>-------------------------------------------------------------------------------</xsl:message>
    <xsl:message>DEBUG OUTPUT:                                                                  </xsl:message>
    <xsl:message>-------------------------------------------------------------------------------</xsl:message>
    <xsl:message></xsl:message>

    <!-- apply all layout templates -->
    <xsl:apply-templates select="$layout/SCRIBUSUTF8NEW" />
  </xsl:template>

  <!-- copy all nodes and attributes -->
  <xsl:template match="@*|*">
	<xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
	</xsl:copy>
  </xsl:template>

  <!-- ################################################################################################# -->
  <!-- ### CLASSIFY PAGEOBJECTS AS SIMPLE OR COMPLEX                                                 ### -->
  <!-- ################################################################################################# -->

  <xsl:template match="PAGEOBJECT">
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:choose>
        <!-- SIMPLE PAGEOBJECTS -->
        <xsl:when test="@ANNAME='title'">
          <xsl:call-template name="simple-pageobject">
            <xsl:with-param name="pageobject-name" select="@ANNAME"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="@ANNAME='subtitle'">
          <xsl:call-template name="simple-pageobject">
            <xsl:with-param name="pageobject-name" select="@ANNAME"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="@ANNAME='blockquote'">
          <xsl:call-template name="simple-pageobject">
            <xsl:with-param name="pageobject-name" select="@ANNAME"/>
          </xsl:call-template>
        </xsl:when>
        <!-- COMPLEX PAGEOBJECTS -->
        <xsl:otherwise>
          <xsl:call-template name="complex-pageobject">
            <xsl:with-param name="pageobject-name" select="@ANNAME"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>


  <!-- SIMPLE PAGEOBJECT -->

  <xsl:template name="simple-pageobject">
    <xsl:param name="pageobject-name" />
    <xsl:message>SIMPLE PAGEOBJECT "<xsl:value-of select="$pageobject-name"/>" FOUND:</xsl:message>
    <xsl:choose>
      <xsl:when test="ITEXT">
        <xsl:message>  +-ITEXT node found</xsl:message>
        <xsl:apply-templates select="child::ITEXT" mode="overwrite-ch">
          <xsl:with-param name="pageobject-name">
            <xsl:value-of select="$pageobject-name"/>
          </xsl:with-param>
        </xsl:apply-templates>
        <xsl:apply-templates select="child::para"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>  +-ITEXT node created</xsl:message>
        <xsl:element name="ITEXT">
          <xsl:attribute name="CH">
            <xsl:value-of select="$content/book/article/*[name()=$pageobject-name]"/>
          </xsl:attribute>
          <xsl:attribute name="SHORTCUT"></xsl:attribute>
          <xsl:attribute name="CNAME">
             <xsl:value-of select="child::ITEXT"/>
          </xsl:attribute>
        </xsl:element>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- OVERWRITE THE CH ATTRIBUTE OF A ITEXT NODE -->

  <xsl:template match="*" mode="overwrite-ch">
    <xsl:param name="pageobject-name"/>
    <xsl:message>    +- overwrite CH attribute</xsl:message>
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:attribute name="CH">
        <xsl:apply-templates select="$content/book/article/*[name()=$pageobject-name]"/>
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>

  <!-- ################################################################################################# -->

  <!--
  <xsl:template match="*[@CH]">
    <xsl:apply-templates select="." mode="copy"/>
  </xsl:template>

  <xsl:template match="*" mode="copy">
    <xsl:copy>
      <xsl:attribute name="CH"><xsl:value-of select="$content/book/article/title"/></xsl:attribute>
      <xsl:apply-templates mode="copy" select="@*[name() != 'CH']"/>
      <xsl:apply-templates mode="copy"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="text()|@*" mode="copy">
    <xsl:copy/>
  </xsl:template>
  -->

  <!-- ################################################################################################# -->

</xsl:stylesheet>