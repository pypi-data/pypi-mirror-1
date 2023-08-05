<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="adr"/>
  <axsl:param name="tel"/>
  <axsl:param name="label"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2333799"/>
  </axsl:template>
  <axsl:template match="item" mode="id2333799">
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
            <axsl:apply-templates select="./card/n/fields/placeholder|./card/n/fields/field" mode="id2338549"/>
          </fields>
        </n>
        <addresses>
          <axsl:apply-templates select="./card/addresses/@*"/>
          <axsl:apply-templates select="./card/addresses/placeholder|./card/addresses/adr" mode="id2338537"/>
        </addresses>
        <telephones>
          <axsl:apply-templates select="./card/telephones/@*"/>
          <axsl:apply-templates select="./card/telephones/placeholder|./card/telephones/tel" mode="id2338491"/>
        </telephones>
        <labels>
          <axsl:apply-templates select="./card/labels/@*"/>
          <axsl:apply-templates select="./card/labels/placeholder|./card/labels/label" mode="id2338687"/>
        </labels>
      </card>
    </item>
  </axsl:template>
  <axsl:template match="field" mode="id2338549">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="adr" mode="id2338537">
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
        <axsl:apply-templates select="./fields/placeholder|./fields/field" mode="id2338643"/>
      </fields>
    </adr>
  </axsl:template>
  <axsl:template match="field" mode="id2338643">
    <field>
      <axsl:apply-templates select="@*"/>
    </field>
  </axsl:template>
  <axsl:template match="tel" mode="id2338491">
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
  <axsl:template match="label" mode="id2338687">
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
  <axsl:template match="placeholder" mode="id2333799">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2331892">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333108">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2331911">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333111">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333129">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2331910">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333491">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333502">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336633">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333485">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338496">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338549">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2333498">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338537">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338478">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338590">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338643">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338628">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338491">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338584">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338550">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338687">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2338699">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
