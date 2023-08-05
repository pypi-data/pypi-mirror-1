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
  <link type="text/css" rel="stylesheet" href="styles/styles.css"/>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="item" mode="id2301139"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2301139">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="card" mode="id2301144"/>
</body>
  </axsl:template>
  <axsl:template match="card" mode="id2301144">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="class" mode="id2301154"/>
    <axsl:apply-templates select="version" mode="id2301170"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="90%">
      <thead>
        <tr>
          <th colspan="3" class="header">
            Contact
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%">
            Formatted name
          </th>
          <td colspan="2">
            <axsl:apply-templates select="fn" mode="id2301241"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            E-mail
          </th>
          <td colspan="2">
            <axsl:apply-templates select="email" mode="id2301274"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Note
          </th>
          <td colspan="2">
            <axsl:apply-templates select="note" mode="id2301306"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Organisation
          </th>
          <td colspan="2">
            <axsl:apply-templates select="org" mode="id2301339"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Role
          </th>
          <td colspan="2">
            <axsl:apply-templates select="role" mode="id2301372"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            URL
          </th>
          <td colspan="2">
            <axsl:apply-templates select="url" mode="id2301404"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="n" mode="id2301424"/>
      <!-- This needs to be outside the "n" element in order to work for empty
           collections. -->
      <tbody>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <input value="Add line" type="submit" name="add-n-field={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="addresses" mode="id2301514"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="Add address" type="submit" name="add-adr={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="telephones" mode="id2301668"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="Add telephone" type="submit" name="add-tel={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
      <axsl:apply-templates select="labels" mode="id2301781"/>
      <tbody>
        <tr>
          <td colspan="3">
            <input value="Add label" type="submit" name="add-label={template:this-element()}"/>
          </td>
        </tr>
        <tr>
          <td colspan="3">
            <input name="save" value="Save changes" type="submit"/>
            <input name="cancel" value="Cancel" type="submit"/>
          </td>
        </tr>
      </tbody>
    </table>
  </form>
  </axsl:template>
  <axsl:template match="class" mode="id2301154">
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
  <axsl:template match="version" mode="id2301170">
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
  <axsl:template match="fn" mode="id2301241">
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
  <axsl:template match="email" mode="id2301274">
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
  <axsl:template match="note" mode="id2301306">
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
  <axsl:template match="org" mode="id2301339">
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
  <axsl:template match="role" mode="id2301372">
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
  <axsl:template match="url" mode="id2301404">
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
  <axsl:template match="n" mode="id2301424">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%">
            Name
          </th>
        </tr>
        <axsl:apply-templates select="fields" mode="id2301441"/>
      </tbody>
  </axsl:template>
  <axsl:template match="fields" mode="id2301441">
    <axsl:apply-templates select="field" mode="id2301441"/>
  </axsl:template>
  <axsl:template match="field" mode="id2301441">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Remove line" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="addresses" mode="id2301514">
    <axsl:apply-templates select="adr" mode="id2301514"/>
  </axsl:template>
  <axsl:template match="adr" mode="id2301514">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%">
            Address
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301572"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301572"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="Remove" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
        <axsl:apply-templates select="fields" mode="id2301545"/>
        <tr>
          <th width="10%">
          </th>
          <td colspan="2">
            <input value="Add line" type="submit" name="add-adr-field={template:this-element()}"/>
          </td>
        </tr>
      </tbody>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2301572">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@type"/>
    </option>
  </axsl:template>
  <axsl:template match="fields" mode="id2301545">
    <axsl:apply-templates select="field" mode="id2301545"/>
  </axsl:template>
  <axsl:template match="field" mode="id2301545">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input size="40" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Remove line" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="telephones" mode="id2301668">
    <axsl:apply-templates select="tel" mode="id2301668"/>
  </axsl:template>
  <axsl:template match="tel" mode="id2301668">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%">
            Telephone
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301727"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301727"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="Remove" type="submit" name="remove={template:this-element()}"/>
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
  <axsl:template match="type-enum" mode="id2301727">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@type"/>
    </option>
  </axsl:template>
  <axsl:template match="labels" mode="id2301781">
    <axsl:apply-templates select="label" mode="id2301781"/>
  </axsl:template>
  <axsl:template match="label" mode="id2301781">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
        <tr>
          <th width="10%">
            Label
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301841"/>
            </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><select value="..." name="{template:this-attribute()}">
              <axsl:apply-templates select="type-enum" mode="id2301841"/>
            </select></axsl:otherwise></axsl:choose>
            <input value="Remove" type="submit" name="remove={template:this-element()}"/>
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
  <axsl:template match="type-enum" mode="id2301841">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@type}">
      <axsl:if test="@type = ../@type">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@type"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
