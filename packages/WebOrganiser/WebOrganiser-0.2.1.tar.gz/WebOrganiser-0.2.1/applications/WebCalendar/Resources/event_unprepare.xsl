<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Ensure proper structure of items. -->

  <xsl:template match="organizers|attendees">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <!-- Replicate unknown nodes. -->

  <xsl:template match="*" priority="0">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|*|node()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
