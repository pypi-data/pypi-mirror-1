<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:apply-templates select="site" mode="id2332986"/>
  </axsl:template>
  <axsl:template match="site" mode="id2332986">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <title><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Calendar Portal']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Calendar Portal</axsl:otherwise></axsl:choose></title>
  <link type="text/css" href="styles/styles.css" rel="stylesheet"/>
</head>
<body>
  <ul class="boxes">
    <li class="header">
      <h1><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Calendar Portal']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Calendar Portal</axsl:otherwise></axsl:choose></h1></li>
    <li class="what">
      <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></h2>
      <p><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='summary-text']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>This page contains a selection of calendar items, presented in a portal-style view.</axsl:otherwise></axsl:choose></p>
      <ul class="leftbox">
        <li class="events">
          <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Events']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Events</axsl:otherwise></axsl:choose></h2>
          <axsl:apply-templates select="events" mode="id2333101"/>
          <p class="more"><a href="">(See the event listings...)</a></p>
        </li>
        <li class="people">
          <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='People']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>People</axsl:otherwise></axsl:choose></h2>
          <axsl:apply-templates select="cards" mode="id2333214"/>
          <p class="more"><a href="">(See the directory...)</a></p>
        </li>
      </ul>
      <ul class="rightbox">
        <li class="tasks">
          <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Tasks']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Tasks</axsl:otherwise></axsl:choose></h2>
          <axsl:apply-templates select="tasks" mode="id2333273"/>
          <p class="more"><a href="">(See more tasks...)</a></p>
        </li>
        <li class="e-mails">
          <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='E-mails']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>E-mails</axsl:otherwise></axsl:choose></h2>
          <axsl:apply-templates select="e-mails" mode="id2333326"/>
          <p class="more"><a href="">(See more entries...)</a></p>
        </li>
        <li class="journals">
          <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Journals']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Journals</axsl:otherwise></axsl:choose></h2>
          <axsl:apply-templates select="journals" mode="id2333379"/>
          <p class="more"><a href="">(See more entries...)</a></p>
        </li>
      </ul>
    </li>
    <li class="what footer"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='configuration-text']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Add configuration options here!</axsl:otherwise></axsl:choose></li>
  </ul>
</body></html>
  </axsl:template>
  <axsl:template match="events" mode="id2333101">
    <ul xmlns="http://www.w3.org/1999/xhtml">
            <axsl:apply-templates select="item" mode="id2333106"/>
          </ul>
  </axsl:template>
  <axsl:template match="item" mode="id2333106">
    <li xmlns="http://www.w3.org/1999/xhtml" class="vevent">
              <a href="" space="preserve">
                <axsl:apply-templates select="summary" mode="id2333124"/>
                (<axsl:apply-templates select="location" mode="id2333142"/>)
              </a>
              <p>
                <axsl:apply-templates select="dtstart" mode="id2333159"/>
                -
                <axsl:apply-templates select="dtend" mode="id2333174"/>
              </p>
            </li>
  </axsl:template>
  <axsl:template match="summary" mode="id2333124">
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
  <axsl:template match="location" mode="id2333142">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="location">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="location">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2333159">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" title="{@value}" class="dtstart">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" title="{@value}" class="dtstart">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtend" mode="id2333174">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" title="{@value}" class="dtend">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" title="{@value}" class="dtend">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="cards" mode="id2333214">
    <ul xmlns="http://www.w3.org/1999/xhtml">
            <axsl:apply-templates select="item" mode="id2333219"/>
          </ul>
  </axsl:template>
  <axsl:template match="item" mode="id2333219">
    <li xmlns="http://www.w3.org/1999/xhtml">
              <a href="">
                <axsl:apply-templates select="fn" mode="id2333230"/>
              </a>
            </li>
  </axsl:template>
  <axsl:template match="fn" mode="id2333230">
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
  <axsl:template match="tasks" mode="id2333273">
    <ul xmlns="http://www.w3.org/1999/xhtml">
            <axsl:apply-templates select="item" mode="id2333278"/>
          </ul>
  </axsl:template>
  <axsl:template match="item" mode="id2333278">
    <li xmlns="http://www.w3.org/1999/xhtml">
              <a href="">
                <axsl:apply-templates select="summary" mode="id2333289"/>
              </a>
            </li>
  </axsl:template>
  <axsl:template match="summary" mode="id2333289">
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
  <axsl:template match="e-mails" mode="id2333326">
    <ul xmlns="http://www.w3.org/1999/xhtml">
            <axsl:apply-templates select="item" mode="id2333331"/>
          </ul>
  </axsl:template>
  <axsl:template match="item" mode="id2333331">
    <li xmlns="http://www.w3.org/1999/xhtml">
              <a href="">
                <axsl:apply-templates select="summary" mode="id2333342"/>
              </a>
            </li>
  </axsl:template>
  <axsl:template match="summary" mode="id2333342">
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
  <axsl:template match="journals" mode="id2333379">
    <ul xmlns="http://www.w3.org/1999/xhtml">
            <axsl:apply-templates select="item" mode="id2333384"/>
          </ul>
  </axsl:template>
  <axsl:template match="item" mode="id2333384">
    <li xmlns="http://www.w3.org/1999/xhtml">
              <a href="">
                <axsl:apply-templates select="summary" mode="id2333395"/>
              </a>
            </li>
  </axsl:template>
  <axsl:template match="summary" mode="id2333395">
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
</axsl:stylesheet>
