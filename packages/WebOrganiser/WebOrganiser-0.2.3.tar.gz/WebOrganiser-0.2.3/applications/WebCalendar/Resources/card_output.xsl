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
<axsl:apply-templates select="item" mode="id2306915"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2306915">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="card" mode="id2306920"/>
</body>
  </axsl:template>
  <axsl:template match="card" mode="id2306920">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="class" mode="id2306930"/>
    <axsl:apply-templates select="version" mode="id2306946"/>
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
            <axsl:apply-templates select="fn" mode="id2307022"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='E-mail']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>E-mail</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="email" mode="id2307055"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Note']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Note</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="note" mode="id2307090"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Organisation']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Organisation</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="org" mode="id2307124"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Role']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Role</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="role" mode="id2307159"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='URL']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>URL</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="url" mode="id2307194"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="n" mode="id2307213"/>
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
      <axsl:apply-templates select="addresses" mode="id2307305"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="{template:i18n('Add address')}" type="submit" name="add-adr={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="telephones" mode="id2307462"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="{template:i18n('Add telephone')}" type="submit" name="add-tel={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="labels" mode="id2307578"/>
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
  <axsl:template match="class" mode="id2306930">
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
  <axsl:template match="version" mode="id2306946">
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
  <axsl:template match="fn" mode="id2307022">
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
  <axsl:template match="email" mode="id2307055">
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
  <axsl:template match="note" mode="id2307090">
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
  <axsl:template match="org" mode="id2307124">
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
  <axsl:template match="role" mode="id2307159">
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
  <axsl:template match="url" mode="id2307194">
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
  <axsl:template match="n" mode="id2307213">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Name']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Name</axsl:otherwise></axsl:choose></th>
        </tr>
        <axsl:apply-templates select="fields" mode="id2307232"/>
      </tbody>
  </axsl:template>
  <axsl:template match="fields" mode="id2307232">
    <axsl:apply-templates select="field" mode="id2307232"/>
  </axsl:template>
  <axsl:template match="field" mode="id2307232">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove line')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="addresses" mode="id2307305">
    <axsl:apply-templates select="adr" mode="id2307305"/>
  </axsl:template>
  <axsl:template match="adr" mode="id2307305">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Address']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Address</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307366"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307366"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
        <axsl:apply-templates select="fields" mode="id2307340"/>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <input value="{template:i18n('Add line')}" type="submit" name="add-adr-field={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2307366">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
  <axsl:template match="fields" mode="id2307340">
    <axsl:apply-templates select="field" mode="id2307340"/>
  </axsl:template>
  <axsl:template match="field" mode="id2307340">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove line')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="telephones" mode="id2307462">
    <axsl:apply-templates select="tel" mode="id2307462"/>
  </axsl:template>
  <axsl:template match="tel" mode="id2307462">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Telephone']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Telephone</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307525"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307525"/>
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
  <axsl:template match="type-enum" mode="id2307525">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
  <axsl:template match="labels" mode="id2307578">
    <axsl:apply-templates select="label" mode="id2307578"/>
  </axsl:template>
  <axsl:template match="label" mode="id2307578">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Label']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Label</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307641"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2307641"/>
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
  <axsl:template match="type-enum" mode="id2307641">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(@type)"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
