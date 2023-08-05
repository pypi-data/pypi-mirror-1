<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Journal</title>
  <link type="text/css" rel="stylesheet" href="{$root}styles/styles.css"/>
  <script type="text/javascript" src="{$root}scripts/sarissa.js"> </script>
  <script type="text/javascript" src="{$root}scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="item" mode="id2289231"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2289231">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="journal" mode="id2289236"/>
</body>
  </axsl:template>
  <axsl:template match="journal" mode="id2289236">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2289248"/>
    <axsl:apply-templates select="dtstamp" mode="id2289262"/>
    <axsl:apply-templates select="sequence" mode="id2289276"/>
    <axsl:apply-templates select="last-modified" mode="id2289290"/>
    <axsl:apply-templates select="class" mode="id2289304"/>
    <axsl:apply-templates select="related-to" mode="id2289318"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
      <thead>
        <tr>
          <th colspan="3" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Journal']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Journal</axsl:otherwise></axsl:choose></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2289393"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Description']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Description</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="description" mode="id2289430"/>
          </td>
        </tr>
        <!-- NOTE: The calendar part originates from the event template. -->
        <tr>
          <th width="10%">
          </th>
          <th width="45%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Start']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Start</axsl:otherwise></axsl:choose></th>
        </tr>
        <tr template:id="datetimes-node" id="{template:this-element()}">
          <th width="10%">
          </th>
          <axsl:apply-templates select="dtstart" mode="id2289484"/>
        </tr>
        <axsl:apply-templates select="organizers" mode="id2289815"/>
        <axsl:apply-templates select="attendees" mode="id2289909"/>
        <axsl:apply-templates select="person-search" mode="id2290021"/>
        <axsl:apply-templates select="person-suggestions" mode="id2290077"/>
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
  <axsl:template match="created" mode="id2289248">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtstamp" mode="id2289262">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="sequence" mode="id2289276">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="last-modified" mode="id2289290">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="class" mode="id2289304">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="related-to" mode="id2289318">
    <axsl:choose>
      <axsl:when test="@uri">
        <axsl:variable name="this-name">uri</axsl:variable>
        <axsl:variable name="this-value" select="@uri"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">uri</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" type="hidden"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="summary" mode="id2289393">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" size="60" type="text"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" size="60" type="text"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="description" mode="id2289430">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <textarea xmlns="http://www.w3.org/1999/xhtml" cols="60" rows="5" name="{template:this-attribute()}">
          <axsl:value-of select="$this-value"/>
        </textarea>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <textarea xmlns="http://www.w3.org/1999/xhtml" cols="60" rows="5" name="{template:this-attribute()}">
          <axsl:value-of select="$this-value"/>
        </textarea>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2289484">
    <td xmlns="http://www.w3.org/1999/xhtml" width="45%" class="calendar">
            <axsl:apply-templates select="month" mode="id2289494"/>
          </td>
  </axsl:template>
  <axsl:template match="month" mode="id2289494">
    <table xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" border="0" align="center">
              <thead>
                <tr>
                  <th colspan="3">
                    <input name="previous-start" value="{template:i18n('Previous')}" type="submit" onclick="return requestUpdate(                         'journal-datetimes',                         'previous-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
                  </th>
                  <th class="month-header" xml:space="preserve">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:variable name="i18n-expr" select="concat('month-', $this-value)"/><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise><axsl:value-of select="$i18n-expr"/></axsl:otherwise></axsl:choose></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                    <!-- Remember the year and month number for navigation. -->
                    <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
                  </th>
                  <th colspan="3">
                    <input name="next-start" value="{template:i18n('Next')}" type="submit" onclick="return requestUpdate(                         'journal-datetimes',                         'next-start,{template:other-attributes('year', .)},{template:other-attributes('number', .)}',                         '{template:other-elements(../..)}',                         '',                         '{template:element-path(template:other-elements(../..))}')                         "/>
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
              <axsl:apply-templates select="week" mode="id2289724"/>
            </table>
  </axsl:template>
  <axsl:template match="week" mode="id2289724">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
                <tr>
                  <axsl:apply-templates select="day" mode="id2289734"/>
                </tr>
                <tr>
                  <!-- Highlight the day if selected. -->
                  <axsl:apply-templates select="day" mode="id2289769"/>
                </tr>
              </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2289734">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-header-fixed">
                    <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
                  </td>
  </axsl:template>
  <axsl:template match="day" mode="id2289769">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum-fixed {template:choice(@start = 'true', 'day-region')} {template:choice(@today = 'true', 'day-today')}">
                    <!-- Refer to the dtstart value attribute. -->
                    <axsl:if test="@date != ''"><input name="{template:other-attributes('datetime', ../../..)}" value="{@date}" type="radio" onclick="return requestUpdate(                         'journal-datetimes',                         '{template:other-attributes('year', ../..)},{template:other-attributes('number', ../..)},{template:other-attributes('datetime', ../../..)}',                         '{template:other-elements(../../../..)}',                         '',                         '{template:element-path(template:other-elements(../../../..))}'                         )"><axsl:if test="@start = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:if>
                  </td>
  </axsl:template>
  <axsl:template match="organizers" mode="id2289815">
    <axsl:apply-templates select="organizer" mode="id2289815"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2289815">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Organiser']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Organiser</axsl:otherwise></axsl:choose></th>
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
  <axsl:template match="attendees" mode="id2289909">
    <axsl:apply-templates select="attendee" mode="id2289909"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2289909">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Attendee']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Attendee</axsl:otherwise></axsl:choose></th>
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
  <axsl:template match="person-search" mode="id2290021">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Person search']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Person search</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@term"><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value" select="@term"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-person" value="{template:i18n('Search')}" type="submit"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="person-suggestions" mode="id2290077">
    <axsl:apply-templates select="card" mode="id2290077"/>
  </axsl:template>
  <axsl:template match="card" mode="id2290077">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:apply-templates select="fn" mode="id2290095"/>
            <axsl:apply-templates select="email" mode="id2290129"/>
            <axsl:apply-templates select="uid" mode="id2290159"/>
            <input value="{template:i18n('Add as organiser')}" type="submit" name="select-organizer={template:this-element()}"/>
            <input value="{template:i18n('Add as attendee')}" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="fn" mode="id2290095">
    <span xmlns="http://www.w3.org/1999/xhtml">
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="email" mode="id2290129">
    <span xmlns="http://www.w3.org/1999/xhtml">
              &lt;<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="uid" mode="id2290159">
    <span xmlns="http://www.w3.org/1999/xhtml">
              (<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
</axsl:stylesheet>
