<xsl:stylesheet version="1.0"
                  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                  xmlns="http://www.w3.org/2000/svg"
                  xmlns:xlink="http://www.w3.org/1999/xlink">

  <!--
       Draws an SVG "tree structure" representing the XSLT/XPath
       infoset of an arbitrary input document.

       Distribute and alter freely.
       Please acknowledge your sources.
       (You could use this stylesheet by importing it into
        your own and overriding its variable settings.)

       Includes a named template from Jeni Tennison's and
       Mike Brown's "ASCII Art" Tree Viewing stylesheet.

       By Wendell Piez, Mulberry Technologies, February 2001.
       Revised July 2001.

  -->


  <xsl:output method="xml" indent="yes" />

  <!-- amend or comment this out if you want to see any
       whitespace-only text nodes -->
  <xsl:strip-space elements="*"/>

  <xsl:param name="across-start" select="6"/>
  <!-- a left margin -->

  <xsl:param name="down-start" select="4"/>
  <!-- a top margin -->

  <xsl:param name="across-interval" select="14"/>
  <!-- size of each horizontal step -->

  <xsl:param name="text-allowance" select="360"/>
  <!-- extra space to the right to allow content of text nodes
       some room -->

  <xsl:param name="max-text-length" select="32"/>
  <!-- maximum number of characters to allow to show of a text node -->

  <xsl:param name="down-interval" select="18"/>
  <!-- size of each vertical step -->

  <xsl:param name="line-thickness" select="1"/>

  <xsl:param name="writing-bump-over" select="6"/>
  <xsl:param name="writing-bump-up" select="-3"/>
  <!-- allow for positioning of node labels -->

  <!-- the following are parameters for styling: -->
  <xsl:param name="background-color" select="'lemonchiffon'"/>

  <xsl:param name="tree-color" select="'#8B4513'"/>

  <xsl:param name="text-font-style"
       select="'font-size: 12; font-family: Courier'"/>

  <xsl:param name="text-color" select="'#8A2BE2'"/>

  <xsl:param name="element-font-style"
       select="'font-size: 14; font-family: serif'"/>

  <xsl:param name="element-color" select="'#006400'"/>

  <xsl:param name="attribute-font-style"
       select="'font-size: 9; font-family: sans-serif'"/>

  <xsl:param name="attribute-color" select="'#4682B4'"/>

  <xsl:param name="code-font-style"
       select="'font-size: 9; font-family: sans-serif'"/>

  <xsl:param name="PI-color" select="'#228B22'"/>

  <xsl:param name="comment-color" select="'#B22222'"/>

  <!-- the following allow adjustments to the symbols
       representing nodes: -->
  <xsl:param name="element-dot-radius" select="2.5"/>

  <xsl:param name="text-box-width" select="3"/>

  <xsl:param name="text-box-height" select="5"/>

  <xsl:variable name="path-style"

 select="concat('stroke:',$tree-color,';fill:none;stroke-width:
 ',$line-thickness,';stroke-linecap:round')"/>

  <!-- calculates the depth of the deepest ancestor
       (so we have an idea of how many levels deep the tree
       will be): a 'max' trick -->
  <xsl:variable name="deepest">
    <!-- returns the depth (in ancestors) of the deepest node(s) -->
    <xsl:for-each select="//node()[not(node())]">
      <xsl:sort select="count(ancestor-or-self::*)"
           order="descending" data-type="number"/>
      <xsl:if test="position()=1">
        <xsl:value-of select="count(ancestor-or-self::*)"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <!-- for the initial viewbox -->
  <xsl:variable name="full-width"
       select="($across-interval * ($deepest +2)) +
                (2 * $across-start) + $text-allowance"/>

  <xsl:variable name="full-height"
       select="((count(//node()) + 2) * $down-interval) +
                (2 * $down-start)"/>

  <xsl:variable name="apos">'</xsl:variable>

  <!-- internal functions to calculate position for any node -->

  <xsl:template name="get-x-coordinate">
    <xsl:param name="node" select="/*"/>
    <xsl:value-of
         select="(count($node/ancestor-or-self::node()) *
                  $across-interval) + $across-start"/>
  </xsl:template>

  <xsl:template name="get-y-coordinate">
    <xsl:param name="node" select="/*"/>
    <xsl:value-of
         select="(count($node/preceding::node()|
                        $node/ancestor-or-self::node()) *
                  $down-interval) + $down-start"/>
  </xsl:template>

  <!-- -->

  <!-- root template -->

  <xsl:template match="/">
    <svg width="{$full-width}" height="{$full-height}" >
      <defs>
        <rect id="text-box" x="0" y="{0 - ($text-box-height div 2)}"
          width="{$text-box-width}" height="{$text-box-height}"
          style="stroke:{$tree-color}; fill:{$tree-color}"/>
        <circle id="element-dot"
          r="{$element-dot-radius}"
          style="stroke:none; fill:{$tree-color}"/>
        <polygon id="pi-marker"
         points="{($text-box-width div 2)} 0, {0 -
 ($text-box-width div 2)}
   {0 - $text-box-width}, {0 - ($text-box-width div 2)}
   {$text-box-width}"
          style="fill:{$tree-color}"/>
        <polygon id="comment-marker"
          points="{0 - ($text-box-width div 2)} 0,
   {($text-box-width div 2)} {0 - $text-box-width},
   {($text-box-width div 2)} {$text-box-width}"
          style="fill:{$tree-color}"/>
      </defs>
      <rect x="0" y="0"
          width="{$full-width}" height="{$full-height}"
          style="fill:{$background-color}"/>
      <g>
        <xsl:apply-templates select="." mode="label">
          <xsl:with-param name="self-x"
              select="$across-start + $across-interval"/>
          <xsl:with-param name="self-y"
              select="$down-start + $down-interval"/>
        </xsl:apply-templates>
        <xsl:apply-templates/>
      </g>
    </svg>
  </xsl:template>

  <!-- -->

  <!-- template for any child node -->

  <xsl:template match="node()">
    <!-- since we're going to draw a line from the parent
         to the node, we first need to ask "do you know
         where your parents are?" -->
    <xsl:variable name="parent-x">
      <xsl:call-template name="get-x-coordinate">
        <xsl:with-param name="node" select=".."/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="parent-y">
      <xsl:call-template name="get-y-coordinate">
        <xsl:with-param name="node" select=".."/>
      </xsl:call-template>
    </xsl:variable>
    <!-- then we need to know where we ourselves are at -->
    <xsl:variable name="self-x">
      <xsl:call-template name="get-x-coordinate">
        <xsl:with-param name="node" select="."/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="self-y">
      <xsl:call-template name="get-y-coordinate">
        <xsl:with-param name="node" select="."/>
      </xsl:call-template>
    </xsl:variable>
    <!-- now we can draw the line -->
    <xsl:call-template name="drawpath">
      <xsl:with-param name="fromX" select="$parent-x"/>
      <xsl:with-param name="fromY" select="$parent-y"/>
      <xsl:with-param name="toX" select="$self-x"/>
      <xsl:with-param name="toY" select="$self-y"/>
    </xsl:call-template>
    <!-- place a label on the node
         (each node type gets a different label) -->
    <xsl:apply-templates select="." mode="label">
      <xsl:with-param name="self-x" select="$self-x"/>
      <xsl:with-param name="self-y" select="$self-y"/>
    </xsl:apply-templates>
    <!-- descend to the next level down -->
    <xsl:apply-templates/>
  </xsl:template>

  <!-- label for each node type -->

  <xsl:template match="*|/" mode="label">
    <xsl:param name="self-x"/>
    <xsl:param name="self-y"/>
    <xsl:if test="..">
      <!-- element nodes get a little dot -->
      <use xlink:href="#element-dot"
   transform="translate({$self-x} {$self-y})"/>
    </xsl:if>
    <text x="{$self-x + $writing-bump-over}"
          y="{$self-y - $writing-bump-up}"
          style="{$element-font-style}; stroke:none;
 fill:{$element-color}">
      <xsl:if test="not(..)">
        <!-- the root node gets labeled with a / -->
        <xsl:text></xsl:text>
      </xsl:if>
      <xsl:value-of select="local-name()"/>
      <xsl:if test="@*">
        <!-- any attribute nodes are written out too -->
        <tspan style="{$attribute-font-style}; stroke:none;
   fill:{$attribute-color}">
          <xsl:for-each select="@*">
              <xsl:text>&#xA0;</xsl:text>
              <xsl:value-of select="local-name()"/>
              <xsl:text>"</xsl:text>
              <xsl:value-of select="."/>
              <xsl:text>"</xsl:text>
          </xsl:for-each>
        </tspan>
      </xsl:if>
    </text>
  </xsl:template>

  <xsl:template match="text()" mode="label">
    <xsl:param name="self-x"/>
    <xsl:param name="self-y"/>
    <xsl:variable name="text" select="normalize-space(.)"/>
    <!-- a quick and dirty way to avoid problems with line breaks -->
    <!-- replace the select attribute with this call
         if you want to use a fancier way to escape whitespace
         characters:
          <xsl:call-template name="escape-ws"
            <xsl:with-param name="text" select="." /
          </xsl:call-template
    -->
    <use xlink:href="#text-box" transform="translate({$self-x}
 {$self-y})"/>
    <!-- text nodes are marked with a little box -->
    <text x="{$self-x + $writing-bump-over}"
          y="{$self-y - $writing-bump-up}"
          style="{$text-font-style}; stroke:none; fill:{$text-color}">
      <xsl:text>"</xsl:text>
      <xsl:value-of select="substring($text,1,$max-text-length)"/>
      <!-- truncate the text node to $max-text-length -->
      <xsl:if test="string-length($text) &gt; $max-text-length">
        <!-- add an ellipsis if necessary -->
        <xsl:text>...</xsl:text>
      </xsl:if>
      <xsl:text>"</xsl:text>
    </text>
  </xsl:template>

  <xsl:template match="processing-instruction()" mode="label">
    <xsl:param name="self-x"/>
    <xsl:param name="self-y"/>
    <!-- PI nodes a marked with a little arrow -->
    <use xlink:href="#pi-marker"
 transform="translate({$self-x} {$self-y})"/>
    <text x="{$self-x + $writing-bump-over}"
          y="{$self-y - $writing-bump-up}"
          style="{$code-font-style}; stroke:none; fill:{$PI-color}">
      <xsl:text>&lt;?</xsl:text>
      <xsl:value-of select="concat(local-name(), ' ', .)"/>
      <xsl:text>&gt;</xsl:text>
    </text>
  </xsl:template>

  <xsl:template match="comment()" mode="label">
    <xsl:param name="self-x"/>
    <xsl:param name="self-y"/>
    <!-- comment nodes are marked with a triangle -->
    <use xlink:href="#comment-marker" transform="translate({$self-x}
 {$self-y})"/>
    <text x="{$self-x + $writing-bump-over}"
          y="{$self-y - $writing-bump-up}"
          style="{$code-font-style}; stroke:none;
 fill:{$comment-color}">
      <xsl:text>&lt;!-- </xsl:text>
      <xsl:value-of select="."/>
      <xsl:text >--&gt;</xsl:text>
    </text>
  </xsl:template>

  <!-- template to draw the line from one node to the next
       ... feel free to enhance ... -->

  <xsl:template name="drawpath">
    <xsl:param name="fromX" select="10"/>
    <xsl:param name="fromY" select="10"/>
    <xsl:param name="toX" select="20"/>
    <xsl:param name="toY" select="20"/>
    <path style="{$path-style}"
          d="M {$fromX} {$fromY} V {$toY} H {$toX}" />
    </xsl:template>


  <!-- recursive template to escape backslashes, apostrophes,
       newlines and tabs -->
  <!-- gratefully duplicated from Jeni Tennison's and Mike Brown's
       ASCII Art-Tree Viewing stylesheet. -->

  <xsl:template name="escape-ws">
    <xsl:param name="text" />
    <xsl:choose>
      <xsl:when test="contains($text, '\')">
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-before($text, '\')" />
        </xsl:call-template>
        <xsl:text>\\</xsl:text>
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-after($text, '\')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($text, $apos)">
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-before($text, $apos)" />
        </xsl:call-template>
        <xsl:text>'</xsl:text>
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-after($text, $apos)" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($text, '&#xA;')">
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-before($text, '&#xA;')" />
        </xsl:call-template>
        <xsl:text>\n</xsl:text>
          <xsl:call-template name="escape-ws">
        <xsl:with-param name="text"
             select="substring-after($text, '&#xA;')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($text, '&#x9;')">
        <xsl:value-of select="substring-before($text, '&#x9;')" />
        <xsl:text>\t</xsl:text>
        <xsl:call-template name="escape-ws">
          <xsl:with-param name="text"
               select="substring-after($text, '&#x9;')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


 </xsl:stylesheet>


