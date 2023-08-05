<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Contact</title>
  <link type="text/css" rel="stylesheet" href="{$root}styles/styles.css"/>
  <script type="text/javascript" src="{$root}scripts/sarissa.js"> </script>
  <script type="text/javascript" src="{$root}scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="item" mode="id2304726"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2304726">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="card" mode="id2304730"/>
</body>
  </axsl:template>
  <axsl:template match="card" mode="id2304730">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="class" mode="id2304740"/>
    <axsl:apply-templates select="version" mode="id2304757"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
      <thead>
        <tr>
          <th colspan="3" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Contact']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Contact</axsl:otherwise></axsl:choose></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Formatted name']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Formatted name</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="fn" mode="id2304832"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='E-mail']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>E-mail</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="email" mode="id2304866"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Note']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Note</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="note" mode="id2304900"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Organisation']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Organisation</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="org" mode="id2304935"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Role']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Role</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="role" mode="id2304970"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='URL']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>URL</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="url" mode="id2305004"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="n" mode="id2305024"/>
      <!-- This needs to be outside the "n" element in order to work for empty
           collections. -->
      <tbody>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <input value="{template:i18n('Add line')}" type="submit" name="add-n-field={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="addresses" mode="id2305115"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="{template:i18n('Add address')}" type="submit" name="add-adr={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="telephones" mode="id2305273"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="{template:i18n('Add telephone')}" type="submit" name="add-tel={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="labels" mode="id2305388"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="{template:i18n('Add label')}" type="submit" name="add-label={template:this-element()}"/>
          </td>
        </tr>
        <tr>
          <td colspan="3">
            <input name="save" value="{template:i18n('Save changes')}" type="submit"/>
            <input name="cancel" value="{template:i18n('Cancel')}" type="submit"/>
          </td>
        </tr>
      </tbody>
    </table>
  </form>
  </axsl:template>
  <axsl:template match="class" mode="id2304740">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="version" mode="id2304757">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="fn" mode="id2304832">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="email" mode="id2304866">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="note" mode="id2304900">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="org" mode="id2304935">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="role" mode="id2304970">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="url" mode="id2305004">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="n" mode="id2305024">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Name']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Name</axsl:otherwise></axsl:choose></th>
        </tr>
        <axsl:apply-templates select="fields" mode="id2305043"/>
      </tbody>
  </axsl:template>
  <axsl:template match="fields" mode="id2305043">
    <axsl:apply-templates select="field" mode="id2305043"/>
  </axsl:template>
  <axsl:template match="field" mode="id2305043">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove line')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="addresses" mode="id2305115">
    <axsl:apply-templates select="adr" mode="id2305115"/>
  </axsl:template>
  <axsl:template match="adr" mode="id2305115">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Address']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Address</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305177"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305177"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
        <axsl:apply-templates select="fields" mode="id2305150"/>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <input value="{template:i18n('Add line')}" type="submit" name="add-adr-field={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2305177">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
  <axsl:template match="fields" mode="id2305150">
    <axsl:apply-templates select="field" mode="id2305150"/>
  </axsl:template>
  <axsl:template match="field" mode="id2305150">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove line')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="telephones" mode="id2305273">
    <axsl:apply-templates select="tel" mode="id2305273"/>
  </axsl:template>
  <axsl:template match="tel" mode="id2305273">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Telephone']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Telephone</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305336"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305336"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          </td>
        </tr>
      </tbody>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2305336">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
  <axsl:template match="labels" mode="id2305388">
    <axsl:apply-templates select="label" mode="id2305388"/>
  </axsl:template>
  <axsl:template match="label" mode="id2305388">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Label']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Label</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305451"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2305451"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          </td>
        </tr>
      </tbody>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2305451">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
