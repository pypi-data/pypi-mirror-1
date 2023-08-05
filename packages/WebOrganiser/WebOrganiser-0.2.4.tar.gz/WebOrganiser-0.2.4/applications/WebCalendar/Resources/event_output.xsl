<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Event</title>
  <link type="text/css" rel="stylesheet" href="{$root}styles/styles.css"/>
  <script type="text/javascript" src="{$root}scripts/sarissa.js"> </script>
  <script type="text/javascript" src="{$root}scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="item" mode="id2299794"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2299794">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="event" mode="id2299799"/>
</body>
  </axsl:template>
  <axsl:template match="event" mode="id2299799">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2299812"/>
    <axsl:apply-templates select="dtstamp" mode="id2299828"/>
    <axsl:apply-templates select="sequence" mode="id2299843"/>
    <axsl:apply-templates select="last-modified" mode="id2299858"/>
    <axsl:apply-templates select="class" mode="id2299872"/>
    <axsl:apply-templates select="priority" mode="id2299885"/>
    <axsl:apply-templates select="transp" mode="id2299899"/>
    <axsl:apply-templates select="related-to" mode="id2299913"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
      <thead>
        <tr>
          <th colspan="3" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Event']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Event']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Event</axsl:otherwise></axsl:choose></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2299986"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Location']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Location']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Location</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="location" mode="id2300020"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
          </th>
          <th width="45%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Start']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Start']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Start</axsl:otherwise></axsl:choose></th>
          <th width="45%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='End']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='End']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>End</axsl:otherwise></axsl:choose></th>
        </tr>
      </tbody>

      <!-- Refreshable datetime area. -->

      <tbody template:id="datetimes-node" id="{template:this-element()}">
        <tr>
          <th width="10%">
          </th>

          <!-- Calendars. -->

          <axsl:apply-templates select="dtstart" mode="id2300088"/>
          <axsl:apply-templates select="dtend" mode="id2300424"/>
        </tr>
      </tbody>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Times']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Times']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Times</axsl:otherwise></axsl:choose></th>

          <!-- Day plans. -->

          <axsl:apply-templates select="dtstart-time" mode="id2300767"/>
          <axsl:apply-templates select="dtend-time" mode="id2300937"/>
        </tr>
      </tbody>
      <tbody>

        <!-- Organiser/attendee. -->

        <axsl:apply-templates select="organizers" mode="id2301094"/>
        <axsl:apply-templates select="attendees" mode="id2301193"/>
        <axsl:apply-templates select="person-search" mode="id2301302"/>
        <axsl:apply-templates select="person-suggestions" mode="id2301343"/>
        <tr>
          <td colspan="3">
            <input name="update" value="{template:i18n('Update')}" type="submit"/>
            <input name="save" value="{template:i18n('Save changes')}" type="submit"/>
            <input name="cancel" value="{template:i18n('Cancel')}" type="submit"/>
          </td>
        </tr>
      </tbody>
    </table>
  </form>
  </axsl:template>
  <axsl:template match="created" mode="id2299812">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtstamp" mode="id2299828">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="sequence" mode="id2299843">
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
  <axsl:template match="last-modified" mode="id2299858">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="class" mode="id2299872">
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
  <axsl:template match="priority" mode="id2299885">
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
  <axsl:template match="transp" mode="id2299899">
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
  <axsl:template match="related-to" mode="id2299913">
    <axsl:choose>
      <axsl:when test="@uri">
        <axsl:variable name="this-name">uri</axsl:variable>
        <axsl:variable name="this-value" select="@uri"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">uri</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="summary" mode="id2299986">
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
  <axsl:template match="location" mode="id2300020">
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
  <axsl:template match="dtstart" mode="id2300088">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2300098"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2300098">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-start" value="{template:i18n('Previous')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'previous-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtend/month)},{template:other-attributes('number', ../../dtend/month)},{template:other-attributes('date', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="month-header" xml:space="preserve">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                    <!-- Remember the year and month number for navigation. -->
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-start" value="{template:i18n('Next')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'next-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtend/month)},{template:other-attributes('number', ../../dtend/month)},{template:other-attributes('date', ../../dtend)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2300333"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2300333">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2300343"/>
                </tr>
                <tr>
                  <!-- Highlight the day if marked. -->
                  <axsl:apply-templates select="day" mode="id2300380"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2300343">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2300380">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(@marked = 'true', 'day-region')} {template:choice(@today = 'true', 'day-today')}">
                    <!-- Refer to the dtstart value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('date', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'event-datetimes',                         '{template:other-attributes('year', ../..)},{template:other-attributes('number', ../..)},{template:other-attributes('date', ../../..)},{template:other-attributes('year', ../../../../dtend/month)},{template:other-attributes('number', ../../../../dtend/month)},{template:other-attributes('date', ../../../../dtend)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="@start = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="dtend" mode="id2300424">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2300432"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2300432">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-end" value="{template:i18n('Previous')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'previous-end,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtstart/month)},{template:other-attributes('number', ../../dtstart/month)},{template:other-attributes('date', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="month-header" xml:space="preserve">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                    <!-- Remember the year and month number for navigation. -->
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-end" value="{template:i18n('Next')}" type="submit" onclick="return requestUpdate(                         'event-datetimes',                         'next-end,{template:other-attributes('year', .)},{template:other-attributes('number', .)},{template:other-attributes('year', ../../dtstart/month)},{template:other-attributes('number', ../../dtstart/month)},{template:other-attributes('date', ../../dtstart)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                </tr>
                <tr>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mon']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Mon']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Mon</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tue']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Tue']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Tue</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Wed']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Wed']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Wed</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Thu']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Thu']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Thu</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Fri']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Fri']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Fri</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sat']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sat']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sat</axsl:otherwise></axsl:choose></th>
                  <th width="14%" class="day-name-header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Sun']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Sun']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Sun</axsl:otherwise></axsl:choose></th>
                </tr>
              </thead>
              <axsl:apply-templates select="week" mode="id2300660"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2300660">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2300669"/>
                </tr>
                <tr>
                  <!-- Highlight the day if marked. -->
                  <axsl:apply-templates select="day" mode="id2300707"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2300669">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2300707">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(@marked = 'true', 'day-region')} {template:choice(@today = 'true', 'day-today')}">
                    <!-- Refer to the dtend value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('date', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'event-datetimes',                         '{template:other-attributes('year', ../..)},{template:other-attributes('number', ../..)},{template:other-attributes('date', ../../..)},{template:other-attributes('year', ../../../../dtstart/month)},{template:other-attributes('number', ../../../../dtstart/month)},{template:other-attributes('date', ../../../../dtstart)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="@end = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="dtstart-time" mode="id2300767">
    <td xmlns="http://www.w3.org/1999/xhtml">
            <div xml:space="preserve">
              <axsl:choose><axsl:when test="@use-time"><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value" select="@use-time"/><input type="radio" value="false" name="{template:this-attribute()}"><axsl:if test="$this-value = 'false'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="false" name="{template:this-attribute()}"><axsl:if test="$this-value = 'false'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose>
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='No start time']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='No start time']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>No start time</axsl:otherwise></axsl:choose></span>
            </div>
            <div xml:space="preserve">
              <axsl:choose><axsl:when test="@use-time"><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value" select="@use-time"/><input type="radio" value="true" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="true" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose>
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Start time given as...']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Start time given as...']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Start time given as...</axsl:otherwise></axsl:choose></span>
              <axsl:apply-templates select="hour" mode="id2300839"/>
              <axsl:apply-templates select="minute" mode="id2300875"/>
              <axsl:apply-templates select="second" mode="id2300903"/>
            </div>
          </td>
  </axsl:template>
  <axsl:template match="hour" mode="id2300839">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="hour-enum" mode="id2300861"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="hour-enum" mode="id2300861"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="hour-enum" mode="id2300861">
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
  <axsl:template match="minute" mode="id2300875">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="minute-enum" mode="id2300889"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="minute-enum" mode="id2300889"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="minute-enum" mode="id2300889">
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
  <axsl:template match="second" mode="id2300903">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="second-enum" mode="id2300917"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="second-enum" mode="id2300917"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="second-enum" mode="id2300917">
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
  <axsl:template match="dtend-time" mode="id2300937">
    <td xmlns="http://www.w3.org/1999/xhtml">
            <div xml:space="preserve">
              <axsl:choose><axsl:when test="@use-time"><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value" select="@use-time"/><input type="radio" value="false" name="{template:this-attribute()}"><axsl:if test="$this-value = 'false'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="false" name="{template:this-attribute()}"><axsl:if test="$this-value = 'false'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose>
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='No end time']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='No end time']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>No end time</axsl:otherwise></axsl:choose></span>
            </div>
            <div xml:space="preserve">
              <axsl:choose><axsl:when test="@use-time"><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value" select="@use-time"/><input type="radio" value="true" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">use-time</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="true" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose>
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='End time given as...']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='End time given as...']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>End time given as...</axsl:otherwise></axsl:choose></span>
              <axsl:apply-templates select="hour" mode="id2300976"/>
              <axsl:apply-templates select="minute" mode="id2301015"/>
              <axsl:apply-templates select="second" mode="id2301051"/>
            </div>
          </td>
  </axsl:template>
  <axsl:template match="hour" mode="id2300976">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="hour-enum" mode="id2301009"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="hour-enum" mode="id2301009"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="hour-enum" mode="id2301009">
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
  <axsl:template match="minute" mode="id2301015">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="minute-enum" mode="id2301037"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="minute-enum" mode="id2301037"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="minute-enum" mode="id2301037">
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
  <axsl:template match="second" mode="id2301051">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="second-enum" mode="id2301064"/>
              </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
                <axsl:apply-templates select="second-enum" mode="id2301064"/>
              </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="second-enum" mode="id2301064">
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
  <axsl:template match="organizers" mode="id2301094">
    <axsl:apply-templates select="organizer" mode="id2301094"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2301094">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Organiser']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Organiser']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Organiser</axsl:otherwise></axsl:choose></th>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@fn"><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value" select="@fn"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            &lt;<axsl:choose><axsl:when test="@email"><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value" select="@email"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
            (<axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
            <axsl:choose><axsl:when test="@fn"><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value" select="@fn"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@email"><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value" select="@email"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="attendees" mode="id2301193">
    <axsl:apply-templates select="attendee" mode="id2301193"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2301193">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Attendee']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Attendee']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Attendee</axsl:otherwise></axsl:choose></th>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@fn"><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value" select="@fn"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            &lt;<axsl:choose><axsl:when test="@email"><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value" select="@email"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
            (<axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
            <axsl:choose><axsl:when test="@fn"><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value" select="@fn"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">fn</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@email"><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value" select="@email"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">email</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="{template:i18n('Remove')}" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="person-search" mode="id2301302">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Person search']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Person search']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Person search</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@term"><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value" select="@term"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-person" value="{template:i18n('Search')}" type="submit"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="person-suggestions" mode="id2301343">
    <axsl:apply-templates select="card" mode="id2301343"/>
  </axsl:template>
  <axsl:template match="card" mode="id2301343">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:apply-templates select="fn" mode="id2301359"/>
            <axsl:apply-templates select="email" mode="id2301393"/>
            <axsl:apply-templates select="uid" mode="id2301423"/>
            <input value="{template:i18n('Add as organiser')}" type="submit" name="select-organizer={template:this-element()}"/>
            <input value="{template:i18n('Add as attendee')}" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="fn" mode="id2301359">
    <span xmlns="http://www.w3.org/1999/xhtml">
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="email" mode="id2301393">
    <span xmlns="http://www.w3.org/1999/xhtml">
              &lt;<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="uid" mode="id2301423">
    <span xmlns="http://www.w3.org/1999/xhtml">
              (<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
</axsl:stylesheet>
