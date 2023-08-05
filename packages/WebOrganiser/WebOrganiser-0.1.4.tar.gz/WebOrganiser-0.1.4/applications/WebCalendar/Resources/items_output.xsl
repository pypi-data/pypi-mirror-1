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
<axsl:apply-templates select="items" mode="id2281624"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2281624">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <div class="buttons">
        <input name="download" type="submit" value="{template:i18n('Download')}"/>
        <input name="download-all" type="submit" value="{template:i18n('Download all')}"/>
        <input name="new-card" type="submit" value="{template:i18n('New card')}"/>
        <input name="new-event" type="submit" value="{template:i18n('New event')}"/>
        <input name="new-journal" type="submit" value="{template:i18n('New journal entry')}"/>
        <input name="new-to-do" type="submit" value="{template:i18n('New to-do item')}"/>
      </div>
      <div class="types" xml:space="preserve">
        <a href="../all"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='all']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>all</axsl:otherwise></axsl:choose></a>
        <a href="../card"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='card']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>card</axsl:otherwise></axsl:choose></a>
        <a href="../event"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='event']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>event</axsl:otherwise></axsl:choose></a>
        <a href="../journal"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='journal']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>journal</axsl:otherwise></axsl:choose></a>
        <a href="../to-do"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='to-do']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>to-do</axsl:otherwise></axsl:choose></a>
        <a href="{template:choice(/items/@filtered, '../../')}../date/{@year-now}/{@month-now}/{template:choice(/items/@filtered, concat(/items/@filter-type, '/', template:url-encode(template:url-encode(/items/@filter-item-value)), '/'))}{@item-type}">
          <img class="image-label" src="images/appointment.png" alt="{template:i18n('Calendar view')}"/>
        </a>
      </div>
      <table class="table-heading" align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th width="10%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Type']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Type</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=@item-type">
                <img class="image-label" src="images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=@item-type&amp;sort-order=descending">
                <img class="image-label" src="images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
            <th width="40%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Summary']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Summary</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=summary/@details">
                <img class="image-label" src="images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=summary/@details&amp;sort-order=descending">
                <img class="image-label" src="images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
            <th width="50%" class="column-header" xml:space="preserve">
              <span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Created']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Created</axsl:otherwise></axsl:choose></span>
              <a href="?sort-by=created/@datetime">
                <img class="image-label" src="images/sort-ascending.png" alt="{template:i18n('Sort ascending')}"/>
              </a>
              <a href="?sort-by=created/@datetime&amp;sort-order=descending">
                <img class="image-label" src="images/sort-descending.png" alt="{template:i18n('Sort descending')}"/>
              </a>
            </th>
          </tr>
        </thead>
      </table>
    </div>
    <axsl:apply-templates select="table" mode="id2281967"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="table" mode="id2281967">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <!-- NOTE: Could put the real headings here. -->
        <thead>
          <tr>
            <th width="10%">
            </th>
            <th width="40%">
            </th>
            <th width="50%">
            </th>
          </tr>
        </thead>

        <!-- Body with hCalendar annotation (translating item types to hCalendar names) -->

        <axsl:apply-templates select="item" mode="id2282022"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="item" mode="id2282022">
    <tbody xmlns="http://www.w3.org/1999/xhtml" class="v{translate(@item-type, '-', '')}">

          <!-- Calendar -->

          <axsl:if test="@item-type = 'calendar'"><tr>
            <!-- Copy this to the item types. -->
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              Calendar
            </td>
            <td>
              <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><a href="?name={template:url-encode($this-value)}"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><a href="?name={template:url-encode($this-value)}"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
          </tr></axsl:if>

          <!-- To-do -->

          <axsl:if test="@item-type = 'to-do' and (not(related-to) or /items/@related-to)"><tr>
            <!-- Copy this to the item types. -->
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/to-do.png" alt="to-do"/>
              </a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/to-do.png" alt="to-do"/>
              </a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="../to-do/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282180"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="../to-do/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282180"/></a></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282208"/>
            </td>
          </tr></axsl:if>

          <!-- Special hidden event and to-do entries for the hCalendar format. -->

          <axsl:if test="(@item-type = 'event' or @item-type = 'to-do' or @item-type = 'journal') and (related-to and not(/items/@related-to))"><tr style="display: none; visibility: collapse">
            <td>
              <axsl:apply-templates select="summary" mode="id2282235"/>
              <axsl:apply-templates select="dtstart" mode="id2282248"/>
              <axsl:apply-templates select="dtend" mode="id2282263"/>
            </td>
          </tr></axsl:if>

          <!-- Event -->

          <axsl:if test="@item-type = 'event' and (not(related-to) or /items/@related-to)"><tr>
            <!-- Copy this to the item types. -->
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/event.png" alt="event"/>
              </a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/event.png" alt="event"/>
              </a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="../event/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282354"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="../event/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282354"/></a></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../../')}../related-to/{template:url-encode(template:url-encode($this-value))}/"><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='(Related)']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>(Related)</axsl:otherwise></axsl:choose></a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282382"/>
            </td>
          </tr></axsl:if>

          <!-- Journal -->

          <axsl:if test="@item-type = 'journal' and (not(related-to) or /items/@related-to)"><tr>
            <!-- Copy this to the item types. -->
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/journal.png" alt="journal"/>
              </a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/journal.png" alt="journal"/>
              </a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="../journal/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282467"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="../journal/{template:url-encode(template:url-encode($this-value))}/">
                <axsl:apply-templates select="summary" mode="id2282467"/></a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282482"/>
            </td>
          </tr></axsl:if>

          <!-- Card -->

          <axsl:if test="@item-type = 'card'"><tr>
            <!-- Copy this to the item types. -->
            <td>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/card.png" alt="card"/>
              </a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="../{template:url-encode($this-value)}/">
                <img class="image-label" src="images/card.png" alt="card"/>
              </a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td xml:space="preserve">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <a href="../person/{template:url-encode(template:url-encode(@item-value))}/">
                <img class="image-label" src="images/search.png" alt="Search"/>
              </a>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="../card/{template:url-encode(template:url-encode($this-value))}/"><axsl:apply-templates select="fn" mode="id2282585"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="../card/{template:url-encode(template:url-encode($this-value))}/"><axsl:apply-templates select="fn" mode="id2282585"/></a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282606"/>
            </td>
          </tr></axsl:if>
        </tbody>
  </axsl:template>
  <axsl:template match="summary" mode="id2282180">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="created" mode="id2282208">
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
  <axsl:template match="summary" mode="id2282235">
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
  <axsl:template match="dtstart" mode="id2282248">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtstart" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtstart" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtend" mode="id2282263">
    <axsl:choose>
      <axsl:when test="@datetime">
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value" select="@datetime"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtend" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">datetime</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml" class="dtend" title="{$this-value}">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="summary" mode="id2282354">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="created" mode="id2282382">
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
  <axsl:template match="summary" mode="id2282467">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="created" mode="id2282482">
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
  <axsl:template match="fn" mode="id2282585">
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
  <axsl:template match="created" mode="id2282606">
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
