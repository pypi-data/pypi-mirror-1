<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Ensure proper structure of items. -->

  <xsl:template match="event|to-do">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="*[local-name() != 'organizer' and local-name() != 'attendee']"/>
      <organizers>
        <xsl:apply-templates select="organizer"/>
      </organizers>
      <attendees>
        <xsl:apply-templates select="attendee"/>
      </attendees>
    </xsl:element>
  </xsl:template>

  <!-- Copy in useful attributes from person definitions. -->

  <xsl:template match="organizer|attendee">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="fn">
        <xsl:value-of select="/item/cards/card[uid/@details=current()/@uri]/fn/@details"/>
      </xsl:attribute>
      <xsl:attribute name="email">
        <xsl:value-of select="/item/cards/card[uid/@details=current()/@uri]/email/@details"/>
      </xsl:attribute>
    </xsl:copy>
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
