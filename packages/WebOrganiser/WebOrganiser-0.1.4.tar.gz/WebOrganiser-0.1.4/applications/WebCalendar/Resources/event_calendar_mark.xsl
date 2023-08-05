<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- NOTE: This is similar to items_calendar_sort.xsl in the processing done. -->
  <!-- Note that the comparison operators convert strings to numbers; we must therefore convert datetimes into dates. -->

  <xsl:template match="day">
    <xsl:variable name="dtstart" select="../../../../dtstart/@datetime"/>
    <xsl:variable name="dtend" select="../../../../dtend/@datetime"/>
    <xsl:variable name="today" select="../../../../dtstart/@today"/>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- Only process calendar cells used as days. -->
      <xsl:if test="@date">
        <xsl:variable name="this-date" select="@date"/>
        <xsl:variable name="next-date" select="number(@date) + 1"/>
        <!-- Set the next date as an attribute. -->
        <xsl:attribute name="next-date"><xsl:value-of select="$next-date"/></xsl:attribute>
        <!-- Find days at or after the event start. -->
        <xsl:if test="substring($dtstart, 1, 8) &lt;= $this-date">
          <!-- Mark days before or at the end of the event. -->
          <xsl:if test="$this-date &lt; substring($dtend, 1, 8) or
            (substring($dtend, 1, 8) = $this-date and substring($dtend, 9, 12))">
            <xsl:attribute name="marked">true</xsl:attribute>
          </xsl:if>
          <!-- Mark the start date. -->
          <xsl:if test="substring($dtstart, 1, 8) = $this-date">
            <xsl:attribute name="start">true</xsl:attribute>
          </xsl:if>
        </xsl:if>
        <!-- Mark the end date. -->
        <xsl:if test="(substring($dtend, 1, 8) = $this-date and substring($dtend, 9, 12)) or
          number(substring($dtend, 1, 8)) = $next-date">
          <xsl:attribute name="end">true</xsl:attribute>
        </xsl:if>
        <!-- Mark today. -->
        <xsl:if test="$this-date = $today">
          <xsl:attribute name="today">true</xsl:attribute>
        </xsl:if>
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
