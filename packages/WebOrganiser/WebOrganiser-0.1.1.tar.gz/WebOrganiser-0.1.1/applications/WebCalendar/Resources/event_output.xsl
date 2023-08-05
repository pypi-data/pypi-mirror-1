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
  <link type="text/css" rel="stylesheet" href="styles/styles.css"/>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="item" mode="id2294260"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2294260">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="event" mode="id2294265"/>
</body>
  </axsl:template>
  <axsl:template match="event" mode="id2294265">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2294277"/>
    <axsl:apply-templates select="dtstamp" mode="id2294293"/>
    <axsl:apply-templates select="sequence" mode="id2294308"/>
    <axsl:apply-templates select="last-modified" mode="id2294323"/>
    <axsl:apply-templates select="class" mode="id2294337"/>
    <axsl:apply-templates select="priority" mode="id2294350"/>
    <axsl:apply-templates select="transp" mode="id2294364"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="90%">
      <thead>
        <tr>
          <th colspan="3" class="header">
            Event
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%">
            Summary
          </th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2294434"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Location
          </th>
          <td colspan="2">
            <axsl:apply-templates select="location" mode="id2294466"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
          </th>
          <th width="45%">
            Start
          </th>
          <th width="45%">
            End
          </th>
        </tr>
        <tr template:id="datetimes-node" id="{template:this-element()}">
          <th width="10%">
          </th>
          <axsl:apply-templates select="dtstart" mode="id2294521"/>
          <axsl:apply-templates select="dtend" mode="id2294810"/>
        </tr>
        <axsl:apply-templates select="organizer-search" mode="id2295089"/>
        <axsl:apply-templates select="organizer-suggestions" mode="id2295128"/>
        <axsl:apply-templates select="organizers" mode="id2295188"/>
        <axsl:apply-templates select="attendee-search" mode="id2295247"/>
        <axsl:apply-templates select="attendee-suggestions" mode="id2295302"/>
        <axsl:apply-templates select="attendees" mode="id2295377"/>
        <tr>
          <td colspan="3">
            <input name="update" value="Update" type="submit"/>
            <input name="save" value="Save changes" type="submit"/>
            <input name="cancel" value="Cancel" type="submit"/>
          </td>
        </tr>
      </tbody>
    </table>
  </form>
  </axsl:template>
  <axsl:template match="created" mode="id2294277">
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
  <axsl:template match="dtstamp" mode="id2294293">
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
  <axsl:template match="sequence" mode="id2294308">
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
  <axsl:template match="last-modified" mode="id2294323">
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
  <axsl:template match="class" mode="id2294337">
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
  <axsl:template match="priority" mode="id2294350">
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
  <axsl:template match="transp" mode="id2294364">
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
  <axsl:template match="summary" mode="id2294434">
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
  <axsl:template match="location" mode="id2294466">
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
  <axsl:template match="dtstart" mode="id2294521">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2294530"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2294530">
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
              <axsl:apply-templates select="week" mode="id2294716"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2294716">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2294726"/>
                </tr>
                <tr>
                  <!-- Highlight the day if the end time occurs during or after the day and if the start time occurs before, on or during the day. -->
                  <!-- Note that the comparison operators convert strings to numbers; we must therefore convert datetimes into dates. -->
                  <axsl:apply-templates select="day" mode="id2294766"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2294726">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2294766">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(substring(../../../../dtend/@datetime, 1, 8) &gt;= @date and                         @date &gt;= substring(../../../@datetime, 1, 8), 'day-region')}">
                    <!-- Refer to the dtstart value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'datetimes',                         '{template:other-attributes('datetime', ../../..)},{template:other-attributes('datetime', ../../../../dtend)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="starts-with(../../../@datetime, @date)"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="dtend" mode="id2294810">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2294819"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2294819">
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
              <axsl:apply-templates select="week" mode="id2294994"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2294994">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2295004"/>
                </tr>
                <tr>
                  <!-- Highlight the day if the end time occurs during or after the day and if the start time occurs before, on or during the day. -->
                  <!-- Note that the comparison operators convert strings to numbers; we must therefore convert datetimes into dates. -->
                  <axsl:apply-templates select="day" mode="id2295044"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2295004">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2295044">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(substring(../../../../dtstart/@datetime, 1, 8) &lt;= @date and                         @date &lt;= substring(../../../@datetime, 1, 8), 'day-region')}">
                    <!-- Refer to the dtend value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'datetimes',                         '{template:other-attributes('datetime', ../../..)},{template:other-attributes('datetime', ../../../../dtstart)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="starts-with(../../../@datetime, @date)"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="organizer-search" mode="id2295089">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
            Organiser search
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-organizer" value="Search" type="submit"/>
            <input value="Add organiser" type="submit" name="select-organizer={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="organizer-suggestions" mode="id2295128">
    <axsl:apply-templates select="organizer-suggestion" mode="id2295128"/>
  </axsl:template>
  <axsl:template match="organizer-suggestion" mode="id2295128">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Add organiser" type="submit" name="select-organizer={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="organizers" mode="id2295188">
    <axsl:apply-templates select="organizer" mode="id2295188"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2295188">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
            Organiser
          </th>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Remove" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="attendee-search" mode="id2295247">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
            Attendee search
          </th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-attendee" value="Search" type="submit"/>
            <input value="Add attendee" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="attendee-suggestions" mode="id2295302">
    <axsl:apply-templates select="attendee-suggestion" mode="id2295302"/>
  </axsl:template>
  <axsl:template match="attendee-suggestion" mode="id2295302">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Add attendee" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="attendees" mode="id2295377">
    <axsl:apply-templates select="attendee" mode="id2295377"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2295377">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%">
            Attendee
          </th>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Remove" type="submit" name="remove={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
</axsl:stylesheet>
