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
<axsl:apply-templates select="item" mode="id2297022"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2297022">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="to-do" mode="id2297027"/>
</body>
  </axsl:template>
  <axsl:template match="to-do" mode="id2297027">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2297039"/>
    <axsl:apply-templates select="dtstamp" mode="id2297054"/>
    <axsl:apply-templates select="sequence" mode="id2297068"/>
    <axsl:apply-templates select="last-modified" mode="id2297082"/>
    <axsl:apply-templates select="class" mode="id2297096"/>
    <axsl:apply-templates select="priority" mode="id2297110"/>
    <axsl:apply-templates select="related-to" mode="id2297125"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
      <thead>
        <tr>
          <th colspan="3" class="header"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='To-do']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='To-do']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>To-do</axsl:otherwise></axsl:choose></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2297198"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Description']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Description']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Description</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="description" mode="id2297234"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Percent complete']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Percent complete']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Percent complete</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="percent-complete" mode="id2297271"/>
          </td>
        </tr>
        <tr>
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Location']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Location']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Location</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:apply-templates select="location" mode="id2297305"/>
          </td>
        </tr>
        <axsl:apply-templates select="organizers" mode="id2297324"/>
        <axsl:apply-templates select="attendees" mode="id2297427"/>
        <axsl:apply-templates select="person-search" mode="id2297539"/>
        <axsl:apply-templates select="person-suggestions" mode="id2297595"/>
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
  <axsl:template match="created" mode="id2297039">
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
  <axsl:template match="dtstamp" mode="id2297054">
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
  <axsl:template match="sequence" mode="id2297068">
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
  <axsl:template match="last-modified" mode="id2297082">
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
  <axsl:template match="class" mode="id2297096">
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
  <axsl:template match="priority" mode="id2297110">
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
  <axsl:template match="related-to" mode="id2297125">
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
  <axsl:template match="summary" mode="id2297198">
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
  <axsl:template match="description" mode="id2297234">
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
  <axsl:template match="percent-complete" mode="id2297271">
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
  <axsl:template match="location" mode="id2297305">
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
  <axsl:template match="organizers" mode="id2297324">
    <axsl:apply-templates select="organizer" mode="id2297324"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2297324">
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
  <axsl:template match="attendees" mode="id2297427">
    <axsl:apply-templates select="attendee" mode="id2297427"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2297427">
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
  <axsl:template match="person-search" mode="id2297539">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th width="10%"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Person search']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Person search']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Person search</axsl:otherwise></axsl:choose></th>
          <td colspan="2">
            <axsl:choose><axsl:when test="@term"><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value" select="@term"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">term</axsl:variable><axsl:variable name="this-value"/><input size="60" type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input name="find-person" value="{template:i18n('Search')}" type="submit"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="person-suggestions" mode="id2297595">
    <axsl:apply-templates select="card" mode="id2297595"/>
  </axsl:template>
  <axsl:template match="card" mode="id2297595">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:apply-templates select="fn" mode="id2297613"/>
            <axsl:apply-templates select="email" mode="id2297647"/>
            <axsl:apply-templates select="uid" mode="id2297678"/>
            <input value="{template:i18n('Add as organiser')}" type="submit" name="select-organizer={template:this-element()}"/>
            <input value="{template:i18n('Add as attendee')}" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="fn" mode="id2297613">
    <span xmlns="http://www.w3.org/1999/xhtml">
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="email" mode="id2297647">
    <span xmlns="http://www.w3.org/1999/xhtml">
              &lt;<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>&gt;
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
  <axsl:template match="uid" mode="id2297678">
    <span xmlns="http://www.w3.org/1999/xhtml">
              (<axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>)
              <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><input type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            </span>
  </axsl:template>
</axsl:stylesheet>
