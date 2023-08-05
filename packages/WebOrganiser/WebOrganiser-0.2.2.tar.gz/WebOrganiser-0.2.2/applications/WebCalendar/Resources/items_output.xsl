<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Items</title>
  <link type="text/css" rel="stylesheet" href="{$root}styles/styles.css"/>
</head>
<axsl:apply-templates select="items" mode="id2280216"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2280216">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <div class="buttons">
        <input name="download" type="submit" value="{template:i18n('Download')}"/>
        <input name="download-all" type="submit" value="{template:i18n('Download all')}"/>
        <input name="new" type="submit" value="{template:i18n('New')}"/>
        <axsl:apply-templates select="new-type" mode="id2280281"/>
      </div>
      <axsl:apply-templates select="item-types" mode="id2280325"/>
      <table class="table-heading" align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th width="10%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Type']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Type</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=@item-type">
                <img class="image-label" src="{$root}images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=@item-type&amp;sort-order=descending">
                <img class="image-label" src="{$root}images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
            <th width="40%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=summary/@details">
                <img class="image-label" src="{$root}images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=summary/@details&amp;sort-order=descending">
                <img class="image-label" src="{$root}images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
            <th width="50%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Created']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Created</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=created/@datetime">
                <img class="image-label" src="{$root}images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=created/@datetime&amp;sort-order=descending">
                <img class="image-label" src="{$root}images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
          </tr>
        </thead>
      </table>
    </div>
    <axsl:apply-templates select="table" mode="id2280543"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="new-type" mode="id2280281">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="new-type-enum" mode="id2280303"/>
        </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="new-type-enum" mode="id2280303"/>
        </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="new-type-enum" mode="id2280303">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:variable name="i18n-expr" select="@value"/>
      <axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/>
      <axsl:choose>
        <axsl:when test="$translation">
          <axsl:value-of select="$translation"/>
        </axsl:when>
        <axsl:otherwise>
          <axsl:value-of select="$i18n-expr"/>
        </axsl:otherwise>
      </axsl:choose>
    </option>
  </axsl:template>
  <axsl:template match="item-types" mode="id2280325">
    <div xmlns="http://www.w3.org/1999/xhtml" class="types" xml:space="preserve">
        <axsl:apply-templates select="item-type" mode="id2280333"/>
        <a href="{template:choice(/items/@filtered, '../../')}../date/{/items/@year-now}/{/items/@month-now}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}">
          <img class="image-label" src="{$root}images/appointment.png" alt="{template:i18n('Calendar view')}"/>
        </a>
      </div>
  </axsl:template>
  <axsl:template match="item-type" mode="id2280333">
    <span xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
          <a href="../{@value}"><axsl:variable name="i18n-expr" select="@value"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></a>
        </span>
  </axsl:template>
  <axsl:template match="table" mode="id2280543">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <!-- NOTE: Could put the real headings here. -->
        <thead>
          <tr>
            <th width="10%">
            </th>
            <th width="40%">
            </th>
            <th width="50%">
            </th>
          </tr>
        </thead>

        <axsl:apply-templates select="item" mode="id2280594"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="item" mode="id2280594">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
          <axsl:if test="not(related-to) or /items/@related-to"><tr>
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="{$root}images/{$this-value}.png" alt="{template:i18n($this-value)}"/>
              </a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="{$root}images/{$this-value}.png" alt="{template:i18n($this-value)}"/>
              </a></axsl:otherwise></axsl:choose>
            </td>
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:if test="fn"><a href="../person/{template:url-encode(template:url-encode(@item-value))}/">
                <img class="image-label" src="{$root}images/search.png" alt="Search"/>
              </a></axsl:if>
              <a href="../{@item-type}/{template:url-encode(template:url-encode(@item-value))}/">
                <axsl:apply-templates select="summary" mode="id2280675"/></a>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="../card/{template:url-encode(template:url-encode($this-value))}/"><axsl:apply-templates select="fn" mode="id2280696"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="../card/{template:url-encode(template:url-encode($this-value))}/"><axsl:apply-templates select="fn" mode="id2280696"/></a></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2280727"/>
            </td>
          </tr></axsl:if>

        </tbody>
  </axsl:template>
  <axsl:template match="summary" mode="id2280675">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="fn" mode="id2280696">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <axsl:value-of select="$this-value"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <axsl:value-of select="$this-value"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="created" mode="id2280727">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
</axsl:stylesheet>
