<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- NOTE: This is similar to items_calendar_sort.xsl in the processing done. -->
  <!-- Note that the comparison operators convert strings to numbers. -->

  <xsl:template match="day">
    <xsl:variable name="dtstart" select="../../../../dtstart/@date"/>
    <xsl:variable name="dtend" select="../../../../dtend/@date"/>
    <xsl:variable name="today" select="../../../../dtstart/@today"/>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- Only process calendar cells used as days. -->
      <xsl:if test="@date">
        <xsl:variable name="this-date" select="@date"/>
        <!-- Find days at or after the event start. -->
        <xsl:if test="$dtstart &lt;= $this-date">
          <!-- Mark days before or at the end of the event. -->
          <xsl:if test="$this-date &lt; $dtend or $dtend = $this-date">
            <xsl:attribute name="marked">true</xsl:attribute>
          </xsl:if>
          <!-- Mark the start date. -->
          <xsl:if test="$dtstart = $this-date">
            <xsl:attribute name="start">true</xsl:attribute>
          </xsl:if>
        </xsl:if>
        <!-- Mark the end date. -->
        <xsl:if test="$dtend = $this-date">
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
