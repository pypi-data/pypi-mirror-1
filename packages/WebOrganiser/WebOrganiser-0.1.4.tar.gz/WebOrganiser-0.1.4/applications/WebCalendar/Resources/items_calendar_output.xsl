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
  <link type="text/css" rel="stylesheet" href="styles/styles.css"/>
</head>
<axsl:apply-templates select="items" mode="id2286166"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2286166">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <div class="buttons">
        <input name="download-all" type="submit" value="{template:i18n('Download all')}"/>
        <input name="new-card" type="submit" value="{template:i18n('New card')}"/>
        <input name="new-event" type="submit" value="{template:i18n('New event')}"/>
        <input name="new-journal" type="submit" value="{template:i18n('New journal entry')}"/>
        <input name="new-to-do" type="submit" value="{template:i18n('New to-do item')}"/>
      </div>
      <div class="types" xml:space="preserve">
        <a href="../all"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='all']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>all</axsl:otherwise></axsl:choose></a>
        <a href="../card"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='card']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>card</axsl:otherwise></axsl:choose></a>
        <a href="../event"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='event']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>event</axsl:otherwise></axsl:choose></a>
        <a href="../journal"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='journal']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>journal</axsl:otherwise></axsl:choose></a>
        <a href="../to-do"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='to-do']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>to-do</axsl:otherwise></axsl:choose></a>
        <a href="{template:choice(/items/@filtered, '../../')}../../../../{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{@item-type}">
          <img class="image-label" src="images/folder.png" alt="{template:i18n('List view')}"/>
        </a>
      </div>
    </div>
    <axsl:apply-templates select="month" mode="id2286315"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="month" mode="id2286315">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th>
              <a href="{template:choice(/items/@filtered, '../../')}../../../{@year-previous}/{@number-previous}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Previous']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Previous</axsl:otherwise></axsl:choose></a>
            </th>
            <th class="header" xml:space="preserve">
              <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="template:i18n(concat('month-', $this-value))"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="template:i18n(concat('month-', $this-value))"/></span></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </th>
            <th>
              <a href="{template:choice(/items/@filtered, '../../')}../../../{@year-next}/{@number-next}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{/items/@item-type}"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Next']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Next</axsl:otherwise></axsl:choose></a>
            </th>
          </tr>
          <tr>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
            <th width="14%" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
          </tr>
        </thead>
        <axsl:apply-templates select="week" mode="id2286486"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="week" mode="id2286486">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
          <tr>
            <axsl:apply-templates select="day" mode="id2286494"/>
          </tr>
          <tr>
            <axsl:apply-templates select="day" mode="id2286518"/>
          </tr>
        </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2286494">
    <td xmlns="http://www.w3.org/1999/xhtml" width="10%" class="{template:choice(@number, 'day-header', 'day-unused')}">
              <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </td>
  </axsl:template>
  <axsl:template match="day" mode="id2286518">
    <td xmlns="http://www.w3.org/1999/xhtml" class="{template:choice(@date, 'day-minimum', 'day-unused')} {template:choice(@marked = 'true', 'day-region')}">

              <!-- Section with hCalendar annotation (translating item types to hCalendar names) -->

              <axsl:apply-templates select="item" mode="id2286531"/>
            </td>
  </axsl:template>
  <axsl:template match="item" mode="id2286531">
    <div xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
                <axsl:if test="substring(created/@datetime, 1, 8) = ../@date"><span>
                  <img src="images/created.png" alt="{template:i18n('Created')}"/>
                </span></axsl:if>
                <axsl:if test="substring(dtstart/@datetime, 1, 8) = ../@date"><span>
                  <img src="images/appointment.png" alt="{template:i18n('Start')}"/>
                </span></axsl:if>
                <axsl:if test="dtstart/@datetime and not(substring(dtstart/@datetime, 1, 8) = ../@date)"><span>
                  <img src="images/continued.png" alt="{template:i18n('Continued')}"/>
                </span></axsl:if>
                <a href="{template:choice(/items/@filtered, '../../')}../{@item-type}/{template:url-encode(template:url-encode(@item-value))}/">
                  <axsl:apply-templates select="summary" mode="id2286597"/>
                </a>
                <axsl:if test="@item-type = 'to-do' or @item-type = 'event' or @item-type = 'journal'"><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode(@item-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:if>
                <axsl:apply-templates select="dtstart" mode="id2286631"/>

                <!-- Special hidden event and to-do entries for the hCalendar format, only for occurring events. -->

                <axsl:if test="substring(dtstart/@datetime, 1, 8) = ../@date"><div class="v{translate(@item-type, '-', '')}" style="display: none; visibility: collapse">
                  <axsl:apply-templates select="dtstart" mode="id2286656"/>
                  <axsl:apply-templates select="dtend" mode="id2286672"/>
                  <axsl:apply-templates select="summary" mode="id2286687"/>
                </div></axsl:if>

              </div>
  </axsl:template>
  <axsl:template match="summary" mode="id2286597">
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
  <axsl:template match="dtstart" mode="id2286631">
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
  <axsl:template match="dtstart" mode="id2286656">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtstart" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtstart" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtend" mode="id2286672">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtend" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtend" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="summary" mode="id2286687">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="summary">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="summary">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
</axsl:stylesheet>
