<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="adr"/>
  <axsl:param name="tel"/>
  <axsl:param name="label"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2330152"/>
  </axsl:template>
  <axsl:template match="item" mode="id2330152">
    <item>
      <axsl:apply-templates select="@*"/>
      <card>
        <axsl:apply-templates select="./card/@*"/>
        <class>
          <axsl:apply-templates select="./card/class/@*"/>
        </class>
        <version>
          <axsl:apply-templates select="./card/version/@*"/>
        </version>
        <fn>
          <axsl:apply-templates select="./card/fn/@*"/>
        </fn>
        <email>
          <axsl:apply-templates select="./card/email/@*"/>
        </email>
        <note>
          <axsl:apply-templates select="./card/note/@*"/>
        </note>
        <org>
          <axsl:apply-templates select="./card/org/@*"/>
        </org>
        <role>
          <axsl:apply-templates select="./card/role/@*"/>
        </role>
        <url>
          <axsl:apply-templates select="./card/url/@*"/>
        </url>
        <n>
          <axsl:apply-templates select="./card/n/@*"/>
          <fields>
            <axsl:apply-templates select="./card/n/fields/@*"/>
            <axsl:apply-templates select="./card/n/fields/placeholder|./card/n/fields/field" mode="id2330346"/>
          </fields>
        </n>
        <addresses>
          <axsl:apply-templates select="./card/addresses/@*"/>
          <axsl:apply-templates select="./card/addresses/placeholder|./card/addresses/adr" mode="id2330276"/>
        </addresses>
        <telephones>
          <axsl:apply-templates select="./card/telephones/@*"/>
          <axsl:apply-templates select="./card/telephones/placeholder|./card/telephones/tel" mode="id2330184"/>
        </telephones>
        <labels>
          <axsl:apply-templates select="./card/labels/@*"/>
          <axsl:apply-templates select="./card/labels/placeholder|./card/labels/label" mode="id2330425"/>
        </labels>
      </card>
    </item>
  </axsl:template>
  <axsl:template match="field" mode="id2330346">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="adr" mode="id2330276">
    <adr>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$adr/adr/type-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
      <fields>
        <axsl:apply-templates select="./fields/@*"/>
        <axsl:apply-templates select="./fields/placeholder|./fields/field" mode="id2330446"/>
      </fields>
    </adr>
  </axsl:template>
  <axsl:template match="field" mode="id2330446">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="tel" mode="id2330184">
    <tel>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$tel/tel/type-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
    </tel>
  </axsl:template>
  <axsl:template match="label" mode="id2330425">
    <label>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$label/label/type-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
    </label>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330152">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330162">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330197">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330205">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330226">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330235">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330241">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330248">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330256">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330262">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330183">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330303">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330346">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330323">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330276">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330344">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330401">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330446">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330289">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330184">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330420">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330251">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330425">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330398">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
