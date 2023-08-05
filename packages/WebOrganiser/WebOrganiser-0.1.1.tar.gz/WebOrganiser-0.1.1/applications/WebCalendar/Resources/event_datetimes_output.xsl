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
          <axsl:apply-templates select="dtstart" mode="id2306290"/>
          <axsl:apply-templates select="dtend" mode="id2306579"/>
        </tr>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2306290">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2306299"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2306299">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-start" value="Previous" type="submit" onclick="return requestUpdate(                         'datetimes',                         'previous-start,{template:other-attributes('datetime', ..)},{template:other-attributes('datetime', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="header">
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>/<axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-start" value="Next" type="submit" onclick="return requestUpdate(                         'datetimes',                         'next-start,{template:other-attributes('datetime', ..)},{template:other-attributes('datetime', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <!-- NOTE: Proper localisation required. -->
                  <th width="14%" class="header">Mon</th>
                  <th width="14%" class="header">Tue</th>
                  <th width="14%" class="header">Wed</th>
                  <th width="14%" class="header">Thu</th>
                  <th width="14%" class="header">Fri</th>
                  <th width="14%" class="header">Sat</th>
                  <th width="14%" class="header">Sun</th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2306485"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2306485">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2306494"/>
                </tr>
                <tr>
                  <!-- Highlight the day if the end time occurs during or after the day and if the start time occurs before, on or during the day. -->
                  <!-- Note that the comparison operators convert strings to numbers; we must therefore convert datetimes into dates. -->
                  <axsl:apply-templates select="day" mode="id2306535"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2306494">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2306535">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(substring(../../../../dtend/@datetime, 1, 8) &gt;= @date and                         @date &gt;= substring(../../../@datetime, 1, 8), 'day-region')}">
                    <!-- Refer to the dtstart value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'datetimes',                         '{template:other-attributes('datetime', ../../..)},{template:other-attributes('datetime', ../../../../dtend)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="starts-with(../../../@datetime, @date)"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="dtend" mode="id2306579">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2306588"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2306588">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-end" value="Previous" type="submit" onclick="return requestUpdate(                         'datetimes',                         'previous-end,{template:other-attributes('datetime', ..)},{template:other-attributes('datetime', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="header">
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>/<axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-end" value="Next" type="submit" onclick="return requestUpdate(                         'datetimes',                         'next-end,{template:other-attributes('datetime', ..)},{template:other-attributes('datetime', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <!-- NOTE: Proper localisation required. -->
                  <th width="14%" class="header">Mon</th>
                  <th width="14%" class="header">Tue</th>
                  <th width="14%" class="header">Wed</th>
                  <th width="14%" class="header">Thu</th>
                  <th width="14%" class="header">Fri</th>
                  <th width="14%" class="header">Sat</th>
                  <th width="14%" class="header">Sun</th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2306762"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2306762">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2306772"/>
                </tr>
                <tr>
                  <!-- Highlight the day if the end time occurs during or after the day and if the start time occurs before, on or during the day. -->
                  <!-- Note that the comparison operators convert strings to numbers; we must therefore convert datetimes into dates. -->
                  <axsl:apply-templates select="day" mode="id2306812"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2306772">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2306812">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(substring(../../../../dtstart/@datetime, 1, 8) &lt;= @date and                         @date &lt;= substring(../../../@datetime, 1, 8), 'day-region')}">
                    <!-- Refer to the dtend value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'datetimes',                         '{template:other-attributes('datetime', ../../..)},{template:other-attributes('datetime', ../../../../dtstart)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="starts-with(../../../@datetime, @date)"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
</axsl:stylesheet>
