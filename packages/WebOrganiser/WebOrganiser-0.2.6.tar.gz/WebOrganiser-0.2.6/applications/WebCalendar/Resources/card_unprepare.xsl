<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- Ensure proper structure of cards. -->

  <xsl:template match="addresses">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="labels">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="telephones">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <!-- Concatenate field information together into a form suitable for storage.
       NOTE: This may be removed later in favour of a Kolab-style representation. -->

  <xsl:template match="*[fields]">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
      <xsl:call-template name="join-fields">
        <xsl:with-param name="field" select="fields/field[2]"/>
        <xsl:with-param name="details" select="fields/field[1]/@value"/>
      </xsl:call-template>
      <xsl:apply-templates select="*[local-name() != 'fields']"/>
    </xsl:element>
  </xsl:template>

  <xsl:template name="join-fields">
    <xsl:param name="field"/>
    <xsl:param name="details"/>
    <xsl:choose>
      <xsl:when test="$field">
        <xsl:call-template name="join-fields">
          <xsl:with-param name="field" select="$field/following-sibling::field[1]"/>
          <xsl:with-param name="details" select="concat($details, ';', $field/@value)"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="details"><xsl:value-of select="$details"/></xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
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
