<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dyn="http://exslt.org/dynamic"
                extension-element-prefixes="dyn"
                version="1.0">

  <xsl:variable name="year" select="/items/month/@year"/>
  <xsl:variable name="month" select="/items/month/@number"/>

  <!-- Do not reproduce the table as is. -->

  <xsl:template match="table">
  </xsl:template>

  <!-- Instead, assign table items to the days of the calendar. -->

  <xsl:template match="day">
    <xsl:variable name="this-date" select="@date"/>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:if test="@date">
        <xsl:apply-templates select="/items/table/item[(substring(dtstart/@datetime, 1, 8) &lt;= $this-date and
          $this-date &lt;= substring(dtend/@datetime, 1, 8)) or substring(created/@datetime, 1, 8) = $this-date]">
          <xsl:sort select="dtstart/@datetime" order="ascending"/>
          <xsl:sort select="created/@datetime" order="ascending"/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:copy>
  </xsl:template>

  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
