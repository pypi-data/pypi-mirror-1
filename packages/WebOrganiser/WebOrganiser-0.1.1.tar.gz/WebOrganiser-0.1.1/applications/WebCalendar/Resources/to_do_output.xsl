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
  <link type="text/css" rel="stylesheet" href="styles/styles.css"/>
</head>
<axsl:apply-templates select="item" mode="id2289887"/>
</html>
  </axsl:template>
  <axsl:template match="item" mode="id2289887">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <axsl:apply-templates select="to-do" mode="id2289892"/>
</body>
  </axsl:template>
  <axsl:template match="to-do" mode="id2289892">
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="POST">
    <axsl:apply-templates select="created" mode="id2289905"/>
    <axsl:apply-templates select="dtstamp" mode="id2289920"/>
    <axsl:apply-templates select="sequence" mode="id2289934"/>
    <axsl:apply-templates select="last-modified" mode="id2289948"/>
    <axsl:apply-templates select="class" mode="id2289962"/>
    <axsl:apply-templates select="priority" mode="id2289976"/>
    <axsl:apply-templates select="transp" mode="id2289990"/>
    <axsl:apply-templates select="related-to" mode="id2290005"/>
    <table align="center" border="0" cellpadding="5" cellspacing="0" width="90%">
      <thead>
        <tr>
          <th colspan="3" class="header">
            To-do
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th width="10%">
            Summary
          </th>
          <td colspan="2">
            <axsl:apply-templates select="summary" mode="id2290075"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Description
          </th>
          <td colspan="2">
            <axsl:apply-templates select="description" mode="id2290110"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Percent complete
          </th>
          <td colspan="2">
            <axsl:apply-templates select="percent-complete" mode="id2290144"/>
          </td>
        </tr>
        <tr>
          <th width="10%">
            Location
          </th>
          <td colspan="2">
            <axsl:apply-templates select="location" mode="id2290176"/>
          </td>
        </tr>
        <axsl:apply-templates select="organizer-search" mode="id2290194"/>
        <axsl:apply-templates select="organizer-suggestions" mode="id2290256"/>
        <axsl:apply-templates select="organizers" mode="id2290315"/>
        <axsl:apply-templates select="attendee-search" mode="id2290361"/>
        <axsl:apply-templates select="attendee-suggestions" mode="id2290431"/>
        <axsl:apply-templates select="attendees" mode="id2290470"/>
        <tr>
          <td colspan="3">
            <input name="save" value="Save changes" type="submit"/>
            <input name="cancel" value="Cancel" type="submit"/>
          </td>
        </tr>
      </tbody>
    </table>
  </form>
  </axsl:template>
  <axsl:template match="created" mode="id2289905">
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
  <axsl:template match="dtstamp" mode="id2289920">
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
  <axsl:template match="sequence" mode="id2289934">
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
  <axsl:template match="last-modified" mode="id2289948">
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
  <axsl:template match="class" mode="id2289962">
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
  <axsl:template match="priority" mode="id2289976">
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
  <axsl:template match="transp" mode="id2289990">
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
  <axsl:template match="related-to" mode="id2290005">
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
  <axsl:template match="summary" mode="id2290075">
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
  <axsl:template match="description" mode="id2290110">
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
  <axsl:template match="percent-complete" mode="id2290144">
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
  <axsl:template match="location" mode="id2290176">
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
  <axsl:template match="organizer-search" mode="id2290194">
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
  <axsl:template match="organizer-suggestions" mode="id2290256">
    <axsl:apply-templates select="organizer-suggestion" mode="id2290256"/>
  </axsl:template>
  <axsl:template match="organizer-suggestion" mode="id2290256">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Add organiser" type="submit" name="select-organizer={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="organizers" mode="id2290315">
    <axsl:apply-templates select="organizer" mode="id2290315"/>
  </axsl:template>
  <axsl:template match="organizer" mode="id2290315">
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
  <axsl:template match="attendee-search" mode="id2290361">
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
  <axsl:template match="attendee-suggestions" mode="id2290431">
    <axsl:apply-templates select="attendee-suggestion" mode="id2290431"/>
  </axsl:template>
  <axsl:template match="attendee-suggestion" mode="id2290431">
    <tr xmlns="http://www.w3.org/1999/xhtml">
          <th/>
          <td colspan="2" xml:space="preserve">
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
            <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><input size="60" type="hidden" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input value="Add attendee" type="submit" name="select-attendee={template:this-element()}"/>
          </td>
        </tr>
  </axsl:template>
  <axsl:template match="attendees" mode="id2290470">
    <axsl:apply-templates select="attendee" mode="id2290470"/>
  </axsl:template>
  <axsl:template match="attendee" mode="id2290470">
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
