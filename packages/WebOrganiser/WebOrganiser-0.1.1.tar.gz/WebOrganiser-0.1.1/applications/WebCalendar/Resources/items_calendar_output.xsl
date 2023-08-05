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
<axsl:apply-templates select="items" mode="id2285733"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2285733">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <input name="download" type="submit" value="Download"/>
      <input name="download-all" type="submit" value="Download all"/>
    </div>
    <axsl:apply-templates select="month" mode="id2285774"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="month" mode="id2285774">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year-previous}/{@number-previous}/{/items/@filter-type}/">Previous</a>
            </th>
            <th class="header">
              <axsl:choose><axsl:when test="@year"><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value" select="@year"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">year</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>/<axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </th>
            <th>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year-next}/{@number-next}/{/items/@filter-type}/">Next</a>
            </th>
            <th xml:space="preserve" colspan="4">
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year}/{@number}/all">all</a>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year}/{@number}/card">card</a>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year}/{@number}/event">event</a>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year}/{@number}/message">message</a>
              <a href="{template:choice(/items/@filtered, '../')}../../../{@year}/{@number}/to-do">to-do</a>
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
        <axsl:apply-templates select="week" mode="id2285968"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="week" mode="id2285968">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
          <tr>
            <axsl:apply-templates select="day" mode="id2285975"/>
          </tr>
          <tr>
            <axsl:apply-templates select="day" mode="id2286000"/>
          </tr>
        </tbody>
  </axsl:template>
  <axsl:template match="day" mode="id2285975">
    <td xmlns="http://www.w3.org/1999/xhtml" width="10%" class="day-header">
              <axsl:choose><axsl:when test="@number"><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value" select="@number"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">number</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
            </td>
  </axsl:template>
  <axsl:template match="day" mode="id2286000">
    <td xmlns="http://www.w3.org/1999/xhtml" class="day-minimum">
              <axsl:apply-templates select="item" mode="id2286007"/>
            </td>
  </axsl:template>
  <axsl:template match="item" mode="id2286007">
    <div xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
                <axsl:if test="substring(created/@datetime, 1, 8) = ../@date"><span>
                  <em>Created:</em>
                </span></axsl:if>
                <a href="{template:choice(/items/@filtered, '../')}../{@item-type}/{template:url-encode(template:url-encode(@item-value))}/">
                  <axsl:apply-templates select="summary" mode="id2286038"/>
                </a>
                <axsl:if test="@item-type = 'to-do'"><a href="{template:choice(/items/@filtered, '../')}../related-to/{template:url-encode(template:url-encode(@item-value))}/">
                  (Related)
                </a></axsl:if>
                <axsl:apply-templates select="dtstart" mode="id2286070"/>
              </div>
  </axsl:template>
  <axsl:template match="summary" mode="id2286038">
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
  <axsl:template match="dtstart" mode="id2286070">
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
