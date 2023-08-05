<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str">

  <!-- Ensure proper structure of cards. -->

  <xsl:template match="*[local-name() = 'card']">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="*[not(local-name() = 'adr') and not(local-name() = 'label') and not(local-name() = 'tel')]"/>
      <addresses>
        <xsl:apply-templates select="*[local-name() = 'adr']"/>
      </addresses>
      <labels>
        <xsl:apply-templates select="*[local-name() = 'label']"/>
      </labels>
      <telephones>
        <xsl:apply-templates select="*[local-name() = 'tel']"/>
      </telephones>
    </xsl:element>
  </xsl:template>

  <xsl:template match="*[local-name() = 'adr' or local-name() = 'n']">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@type"/>
      <xsl:call-template name="make-fields"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="*[local-name() = 'label' or local-name() = 'tel']">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
    </xsl:element>
  </xsl:template>

  <xsl:template name="make-fields">
    <fields>
      <xsl:for-each select="str:split(@details, ';')">
        <field value="{string(.)}"/>
      </xsl:for-each>
    </fields>
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
