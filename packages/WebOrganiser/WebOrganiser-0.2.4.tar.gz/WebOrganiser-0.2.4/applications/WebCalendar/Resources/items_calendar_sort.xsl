<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Do not reproduce the table as is. -->

  <xsl:template match="table">
  </xsl:template>

  <!-- Instead, assign table items to the days of the calendar. -->

  <xsl:template match="day">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- Only process calendar cells representing actual days. -->
      <xsl:if test="@date">
        <xsl:variable name="this-date" select="@date"/>
        <xsl:variable name="created-items" select="/items/table/item[substring(created/@datetime, 1, 8) = $this-date]"/>
        <xsl:variable name="updated-items" select="/items/table/item[substring(last-modified/@datetime, 1, 8) = $this-date]"/>
        <xsl:variable name="occurring-items" select="/items/table/item[
          (substring(dtstart/@datetime, 1, 8) &lt;= $this-date and $this-date &lt; substring(dtend/@datetime, 1, 8)) or
          (substring(dtend/@datetime, 1, 8) = $this-date and substring(dtend/@datetime, 9, 12))]"/>
        <!-- Provide marking of the calendar for days having occuring items. -->
        <xsl:if test="$occurring-items">
          <xsl:attribute name="marked">true</xsl:attribute>
        </xsl:if>
        <xsl:variable name="single-day-items" select="/items/table/item[substring(dtstart/@datetime, 1, 8) = $this-date and not(dtend)]"/>
        <!-- Copy details of items into days on which they occur or were created. -->
        <xsl:apply-templates select="$created-items|$updated-items|$occurring-items|$single-day-items">
          <xsl:sort select="dtstart/@datetime" order="ascending"/>
          <xsl:sort select="created/@datetime" order="ascending"/>
          <xsl:sort select="last-modified/@datetime" order="ascending"/>
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
