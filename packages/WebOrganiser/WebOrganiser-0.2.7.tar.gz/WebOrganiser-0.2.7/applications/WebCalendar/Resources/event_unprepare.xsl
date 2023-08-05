<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Ensure proper structure of items. -->

  <xsl:template match="dtstart|dtend">
    <xsl:call-template name="dt">
      <xsl:with-param name="time-name" select="concat(local-name(), '-time')"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="dt">
    <xsl:param name="time-name"/>
    <xsl:variable name="hour" select="../*[local-name() = $time-name]/hour/@value"/>
    <xsl:variable name="minute" select="../*[local-name() = $time-name]/minute/@value"/>
    <xsl:variable name="second" select="../*[local-name() = $time-name]/second/@value"/>
    <xsl:variable name="use-time" select="../*[local-name() = $time-name]/@use-time"/>
    <xsl:copy>
      <xsl:choose>
        <xsl:when test="$use-time = 'false'">
          <xsl:attribute name="datetime"><xsl:value-of select="@date"/></xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="datetime"><xsl:value-of select="@date"/>T<xsl:value-of select="$hour"/><xsl:value-of select="$minute"/><xsl:value-of select="$second"/></xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

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
