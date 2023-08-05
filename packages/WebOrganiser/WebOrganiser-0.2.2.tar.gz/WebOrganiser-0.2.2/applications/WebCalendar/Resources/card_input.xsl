<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="adr"/>
  <axsl:param name="tel"/>
  <axsl:param name="label"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2319404"/>
  </axsl:template>
  <axsl:template match="item" mode="id2319404">
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
            <axsl:apply-templates select="./card/n/fields/placeholder|./card/n/fields/field" mode="id2323811"/>
          </fields>
        </n>
        <addresses>
          <axsl:apply-templates select="./card/addresses/@*"/>
          <axsl:apply-templates select="./card/addresses/placeholder|./card/addresses/adr" mode="id2323806"/>
        </addresses>
        <telephones>
          <axsl:apply-templates select="./card/telephones/@*"/>
          <axsl:apply-templates select="./card/telephones/placeholder|./card/telephones/tel" mode="id2323923"/>
        </telephones>
        <labels>
          <axsl:apply-templates select="./card/labels/@*"/>
          <axsl:apply-templates select="./card/labels/placeholder|./card/labels/label" mode="id2323905"/>
        </labels>
      </card>
    </item>
  </axsl:template>
  <axsl:template match="field" mode="id2323811">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="adr" mode="id2323806">
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
        <axsl:apply-templates select="./fields/placeholder|./fields/field" mode="id2323910"/>
      </fields>
    </adr>
  </axsl:template>
  <axsl:template match="field" mode="id2323910">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="tel" mode="id2323923">
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
  <axsl:template match="label" mode="id2323905">
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
  <axsl:template match="placeholder" mode="id2319404">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323623">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323660">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323652">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323690">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323697">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323705">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323710">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323717">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323724">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323708">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323766">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323811">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323812">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323806">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323735">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323864">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323910">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323715">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323923">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323846">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323900">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323905">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323936">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
