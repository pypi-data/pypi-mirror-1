<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <tr xmlns="http://www.w3.org/1999/xhtml" template:id="datetimes-node" id="{template:this-element()}">
          <th width="10%">
          </th>
          <axsl:apply-templates select="dtstart" mode="id2315868"/>
          <axsl:apply-templates select="dtend" mode="id2316204"/>
        </tr>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2315868">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2315877"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2315877">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-start" value="{template:i18n('Previous')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'previous-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtend/month)},{template:other-attributes('number', ../../dtend/month)},{template:other-attributes('datetime', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="month-header" xml:space="preserve">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                    <!-- Remember the year and month number for navigation. -->
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-start" value="{template:i18n('Next')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'next-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtend/month)},{template:other-attributes('number', ../../dtend/month)},{template:other-attributes('datetime', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2316112"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2316112">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2316122"/>
                </tr>
                <tr>
                  <!-- Highlight the day if marked. -->
                  <axsl:apply-templates select="day" mode="id2316160"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2316122">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2316160">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(@marked = 'true', 'day-region')} {template:choice(@today = 'true', 'day-today')}">
                    <!-- Refer to the dtstart value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'event-datetimes',                         '{template:other-attributes('year', ../..)},{template:other-attributes('number', ../..)},{template:other-attributes('datetime', ../../..)},{template:other-attributes('year', ../../../../dtend/month)},{template:other-attributes('number', ../../../../dtend/month)},{template:other-attributes('datetime', ../../../../dtend)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="@start = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="dtend" mode="id2316204">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2316212"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2316212">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-end" value="{template:i18n('Previous')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'previous-end,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtstart/month)},{template:other-attributes('number', ../../dtstart/month)},{template:other-attributes('datetime', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="month-header" xml:space="preserve">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                    <!-- Remember the year and month number for navigation. -->
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-end" value="{template:i18n('Next')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'next-end,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtstart/month)},{template:other-attributes('number', ../../dtstart/month)},{template:other-attributes('datetime', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2316440"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2316440">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2316450"/>
                </tr>
                <tr>
                  <!-- Highlight the day if marked. -->
                  <axsl:apply-templates select="day" mode="id2316487"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2316450">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2316487">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(@marked = 'true', 'day-region')} {template:choice(@today = 'true', 'day-today')}">
                    <!-- Refer to the dtend value attribute. -->
                    <axsl:if test="@next-date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@next-date}" type="radio" onclick="return requestUpdate(                         'event-datetimes',                         '{template:other-attributes('year', ../..)},{template:other-attributes('number', ../..)},{template:other-attributes('datetime', ../../..)},{template:other-attributes('year', ../../../../dtstart/month)},{template:other-attributes('number', ../../../../dtstart/month)},{template:other-attributes('datetime', ../../../../dtstart)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="@end = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
</axsl:stylesheet>
