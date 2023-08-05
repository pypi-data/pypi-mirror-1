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
<axsl:apply-templates select="items" mode="id2283867"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2283867">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <div class="buttons">
        <input name="download-all" type="submit" value="{template:i18n('Download all')}"/>
        <input name="new" type="submit" value="{template:i18n('New')}"/>
        <axsl:apply-templates select="new-type" mode="id2283922"/>
      </div>
      <axsl:apply-templates select="item-types" mode="id2283966"/>
    </div>
    <axsl:apply-templates select="month" mode="id2284012"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="new-type" mode="id2283922">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="new-type-enum" mode="id2283944"/>
        </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="new-type-enum" mode="id2283944"/>
        </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="new-type-enum" mode="id2283944">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:variable name="i18n-expr" select="@value"/>
      <axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/>
      <axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/>
      <axsl:choose>
        <axsl:when test="$translation">
          <axsl:value-of select="$translation"/>
        </axsl:when>
        <axsl:when test="$translation-default">
          <axsl:value-of select="$translation-default"/>
        </axsl:when>
        <axsl:otherwise>
          <axsl:value-of select="$i18n-expr"/>
        </axsl:otherwise>
      </axsl:choose>
    </option>
  </axsl:template>
  <axsl:template match="item-types" mode="id2283966">
    <div xmlns="http://www.w3.org/1999/xhtml" class="types" xml:space="preserve">
        <axsl:apply-templates select="item-type" mode="id2283974"/>
        <a href="{template:choice(/items/@filtered, '../../')}../../../../{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}">
          <img class="image-label" src="{$root}images/folder.png" alt="{template:i18n('List view')}"/>
        </a>
      </div>
  </axsl:template>
  <axsl:template match="item-type" mode="id2283974">
    <span xmlns="http://www.w3.org/1999/xhtml" class="{template:choice(/items/@item-type = @value or not(/items/@item-type) and @value = 'all', 'type-selected', 'type')}">
          <a href="../{@value}"><axsl:variable name="i18n-expr" select="@value"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></a>
        </span>
  </axsl:template>
  <axsl:template match="month" mode="id2284012">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th>
              <a href="{template:choice(/items/@filtered, '../../')}../../../{@year-previous}/{@number-previous}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Previous']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Previous']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Previous</axsl:otherwise></axsl:choose></a>
            </th>
            <th class="header" xml:space="preserve">
              <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="template:i18n(concat('month-', $this-value))"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="template:i18n(concat('month-', $this-value))"/></span></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </th>
            <th>
              <a href="{template:choice(/items/@filtered, '../../')}../../../{@year-next}/{@number-next}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Next']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Next']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Next</axsl:otherwise></axsl:choose></a>
            </th>
          </tr>
          <tr>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
          </tr>
        </thead>
        <axsl:apply-templates select="week" mode="id2284178"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="week" mode="id2284178">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
          <tr>
            <axsl:apply-templates select="day" mode="id2284186"/>
          </tr>
          <tr>
            <axsl:apply-templates select="day" mode="id2284210"/>
          </tr>
        </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2284186">
    <td xmlns="http://www.w3.org/1999/xhtml" width="10%" class="{template:choice(@number, 'day-header', 'day-unused')}">
              <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </td>
  </axsl:template>
  <axsl:template match="day" mode="id2284210">
    <td xmlns="http://www.w3.org/1999/xhtml" class="{template:choice(@date, 'day-minimum', 'day-unused')} {template:choice(@marked = 'true', 'day-region')}">

              <axsl:apply-templates select="item" mode="id2284219"/>
            </td>
  </axsl:template>
  <axsl:template match="item" mode="id2284219">
    <div xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
                <axsl:if test="substring(created/@datetime, 1, 8) = ../@date"><span>
                  <img src="{$root}images/created.png" alt="{template:i18n('Created')}"/>
                </span></axsl:if>
                <axsl:if test="substring(last-modified/@datetime, 1, 8) = ../@date"><span>
                  <img src="{$root}images/updated.png" alt="{template:i18n('Updated')}"/>
                </span></axsl:if>
                <axsl:if test="substring(dtstart/@datetime, 1, 8) = ../@date"><span>
                  <img src="{$root}images/appointment.png" alt="{template:i18n('Start')}"/>
                </span></axsl:if>
                <axsl:if test="dtstart/@datetime and not(substring(dtstart/@datetime, 1, 8) = ../@date) and                                    not(substring(created/@datetime, 1, 8) = ../@date) and                                    not(substring(last-modified/@datetime, 1, 8) = ../@date)"><span>
                  <img src="{$root}images/continued.png" alt="{template:i18n('Continued')}"/>
                </span></axsl:if>
                <a href="{template:choice(/items/@filtered, '../../')}../{@item-type}/{template:url-encode(template:url-encode(@item-value))}/">
                  <axsl:apply-templates select="summary" mode="id2283958"/>
                </a>
                <a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode(@item-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a>
                <axsl:apply-templates select="dtstart" mode="id2284321"/>

              </div>
  </axsl:template>
  <axsl:template match="summary" mode="id2283958">
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
  <axsl:template match="dtstart" mode="id2284321">
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
