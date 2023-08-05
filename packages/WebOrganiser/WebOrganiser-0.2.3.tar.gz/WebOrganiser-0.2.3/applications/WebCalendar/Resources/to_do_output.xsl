<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>To-do</title>
  <link type="text/css" rel="stylesheet" href="{$root}styles/styles.css"/>
</head>
<axsl:apply-templates select="item" mode="id2296049"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2296049">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="to-do" mode="id2296054"/>
</body>
  </axsl:template>
  <axsl:template match="to-do" mode="id2296054">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2296066"/>
    <axsl:apply-templates select="dtstamp" mode="id2296080"/>
    <axsl:apply-templates select="sequence" mode="id2296095"/>
    <axsl:apply-templates select="last-modified" mode="id2296109"/>
    <axsl:apply-templates select="class" mode="id2296123"/>
    <axsl:apply-templates select="priority" mode="id2296137"/>
    <axsl:apply-templates select="related-to" mode="id2296151"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
      <thead>
        <tr>
          <th colspan="3" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='To-do']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>To-do</axsl:otherwise></axsl:choose></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2296224"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Description']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Description</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="description" mode="id2296261"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Percent complete']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Percent complete</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="percent-complete" mode="id2296297"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Location']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Location</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="location" mode="id2296332"/>
          </td>
        </tr>
        <axsl:apply-templates select="organizers" mode="id2296351"/>
        <axsl:apply-templates select="attendees" mode="id2296454"/>
        <axsl:apply-templates select="person-search" mode="id2296566"/>
        <axsl:apply-templates select="person-suggestions" mode="id2296621"/>
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
  <axsl:template match="created" mode="id2296066">
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
  <axsl:template match="dtstamp" mode="id2296080">
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
  <axsl:template match="sequence" mode="id2296095">
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
  <axsl:template match="last-modified" mode="id2296109">
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
  <axsl:template match="class" mode="id2296123">
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
  <axsl:template match="priority" mode="id2296137">
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
  <axsl:template match="related-to" mode="id2296151">
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
  <axsl:template match="summary" mode="id2296224">
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
  <axsl:template match="description" mode="id2296261">
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
  <axsl:template match="percent-complete" mode="id2296297">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" size="5" type="text"/>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <input xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}" value="{$this-value}" size="5" type="text"/>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="location" mode="id2296332">
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
  <axsl:template match="organizers" mode="id2296351">
    <axsl:apply-templates select="organizer" mode="id2296351"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2296351">
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
  <axsl:template match="attendees" mode="id2296454">
    <axsl:apply-templates select="attendee" mode="id2296454"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2296454">
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
  <axsl:template match="person-search" mode="id2296566">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Person search']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Person search</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@term"><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value" select="@term"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-person" value="{template:i18n('Search')}" type="submit"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="person-suggestions" mode="id2296621">
    <axsl:apply-templates select="card" mode="id2296621"/>
  </axsl:template>
  <axsl:template match="card" mode="id2296621">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:apply-templates select="fn" mode="id2296640"/>
            <axsl:apply-templates select="email" mode="id2296674"/>
            <axsl:apply-templates select="uid" mode="id2296704"/>
            <input value="{template:i18n('Add as organiser')}" type="submit" name="select-organizer={template:this-element()}"/>
            <input value="{template:i18n('Add as attendee')}" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="fn" mode="id2296640">
    <span xmlns="http://www.w3.org/1999/xhtml">
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="email" mode="id2296674">
    <span xmlns="http://www.w3.org/1999/xhtml">
              &lt;<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="uid" mode="id2296704">
    <span xmlns="http://www.w3.org/1999/xhtml">
              (<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
</axsl:stylesheet>
