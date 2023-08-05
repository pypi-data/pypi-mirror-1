<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dyn="http://exslt.org/dynamic"
                extension-element-prefixes="dyn"
                version="1.0">

  <xsl:param name="sort-by"/>
  <xsl:param name="sort-order">ascending</xsl:param>

  <!-- Sort the rows of the table. -->

  <xsl:template match="table">
    <!-- Copy the element and its contents. -->
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- Sort the contents. -->
      <xsl:apply-templates select="item">
        <xsl:sort select="dyn:evaluate($sort-by)" order="{$sort-order}"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
