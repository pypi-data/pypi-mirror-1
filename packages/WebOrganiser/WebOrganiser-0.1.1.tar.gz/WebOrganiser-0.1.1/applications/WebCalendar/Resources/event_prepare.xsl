<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Ensure proper structure of items. -->

  <xsl:template match="*[local-name() = 'event' or local-name() = 'to-do']">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="*[local-name() != 'organizer' and local-name() != 'attendee']"/>
      <organizers>
        <xsl:apply-templates select="*[local-name() = 'organizer']"/>
      </organizers>
      <attendees>
        <xsl:apply-templates select="*[local-name() = 'attendee']"/>
      </attendees>
    </xsl:element>
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
