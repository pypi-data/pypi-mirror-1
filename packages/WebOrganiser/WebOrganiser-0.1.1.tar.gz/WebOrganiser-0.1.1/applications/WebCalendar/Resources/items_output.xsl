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
<axsl:apply-templates select="items" mode="id2281483"/>
</html>
  </axsl:template>
  <axsl:template match="items" mode="id2281483">
    <body xmlns="http://www.w3.org/1999/xhtml">
  <form action="" method="POST">
    <div class="controls">
      <input name="download" type="submit" value="Download"/>
      <input name="download-all" type="submit" value="Download all"/>
      <input name="new-event" type="submit" value="New event"/>
      <input name="new-to-do" type="submit" value="New to-do item"/>
      <input name="new-card" type="submit" value="New card"/>
    </div>
    <axsl:apply-templates select="table" mode="id2281552"/>
  </form>
</body>
  </axsl:template>
  <axsl:template match="table" mode="id2281552">
    <div xmlns="http://www.w3.org/1999/xhtml" class="view">
      <table align="center" border="0" cellpadding="5" cellspacing="0" width="100%">
        <thead>
          <tr>
            <th width="10%" class="header" xml:space="preserve">
              <a href="?sort-by=@item-type">Type</a>
              <a href="?sort-by=@item-type&amp;sort-order=descending">(D)</a>
            </th>
            <th class="header" xml:space="preserve">
              <a href="?sort-by=summary/@details">Summary</a>
              <a href="?sort-by=summary/@details&amp;sort-order=descending">(D)</a>
            </th>
            <th class="header" xml:space="preserve">
              <a href="?sort-by=created/@datetime">Created</a>
              <a href="?sort-by=created/@datetime&amp;sort-order=descending">(D)</a>
            </th>
          </tr>
        </thead>

        <!-- Body with hCalendar annotation (translating item types to hCalendar names) -->

        <axsl:apply-templates select="item" mode="id2281661"/>
      </table>
    </div>
  </axsl:template>
  <axsl:template match="item" mode="id2281661">
    <tbody xmlns="http://www.w3.org/1999/xhtml" class="v{translate(@item-type, '-', '')}">

          <!-- Calendar -->

          <axsl:if test="@item-type = 'calendar'"><tr>
            <!-- Copy this to the item types. -->
            <td width="10%">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:choice(/items/@filtered, '../')}{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td class="row-header">
              Calendar
            </td>
            <td class="row-header">
              <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><a href="?name={template:url-encode($this-value)}"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><a href="?name={template:url-encode($this-value)}"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
          </tr></axsl:if>

          <!-- To-do (with hCalendar annotations within certain column elements) -->

          <axsl:if test="@item-type = 'to-do' and (not(related-to) or /items/@related-to)"><tr>
            <!-- Copy this to the item types. -->
            <td width="10%">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td class="row-header">
              <axsl:apply-templates select="organizer" mode="id2281815"/>
            </td>
            <td class="row-header">
              <axsl:apply-templates select="dtstart" mode="id2281847"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'to-do' and (not(related-to) or /items/@related-to)"><tr>
            <td/>
            <td xml:space="preserve">
              <axsl:apply-templates select="summary" mode="id2281877"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../')}../to-do/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../to-do/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../')}../related-to/{template:url-encode(template:url-encode($this-value))}/">(Related)</a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../related-to/{template:url-encode(template:url-encode($this-value))}/">(Related)</a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2281914"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'to-do' and (not(related-to) or /items/@related-to)"><tr>
            <td/>
            <axsl:apply-templates select="description" mode="id2281935"/>
          </tr></axsl:if>

          <!-- Special hidden to-do entries for the hCalendar format. -->

          <axsl:if test="@item-type = 'to-do' and (related-to and not(/items/@related-to))"><tr style="display: none; visibility: collapse">
            <td>
              <axsl:apply-templates select="dtstart" mode="id2281967"/>
              <axsl:apply-templates select="summary" mode="id2281982"/>
            </td>
          </tr></axsl:if>

          <!-- Event (with hCalendar annotations within certain column elements) -->

          <axsl:if test="@item-type = 'event'"><tr>
            <!-- Copy this to the item types. -->
            <td width="10%">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td class="row-header">
              <axsl:apply-templates select="organizer" mode="id2282059"/>
            </td>
            <td class="row-header" xml:space="preserve">
              <axsl:apply-templates select="dtstart" mode="id2282089"/>
              to
              <axsl:apply-templates select="dtend" mode="id2282104"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'event'"><tr>
            <td/>
            <td xml:space="preserve">
              <axsl:apply-templates select="summary" mode="id2282133"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../')}../event/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../event/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282160"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'event'"><tr>
            <td/>
            <axsl:apply-templates select="description" mode="id2282181"/>
          </tr></axsl:if>

          <!-- Message -->

          <axsl:if test="@item-type = 'message'"><tr>
            <!-- Copy this to the item types. -->
            <td width="10%">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td class="row-header">
              <axsl:apply-templates select="sender" mode="id2282258"/>
            </td>
            <td class="row-header">
              <axsl:apply-templates select="sender" mode="id2282279"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'message'"><tr>
            <td/>
            <td>
              Text message
            </td>
            <td>
              <axsl:apply-templates select="created" mode="id2282304"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'message'"><tr>
            <td/>
            <axsl:apply-templates select="body" mode="id2282325"/>
          </tr></axsl:if>

          <!-- Card -->

          <axsl:if test="@item-type = 'card'"><tr>
            <!-- Copy this to the item types. -->
            <td width="10%">
              <input name="item={template:this-element()}" value="1" type="checkbox"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><input name="{template:this-attribute()}" value="{$this-value}" type="hidden"/></axsl:otherwise></axsl:choose>
              <axsl:choose><axsl:when test="@item-type"><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value" select="@item-type"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-type</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../{template:url-encode($this-value)}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
            </td>
            <!-- End generic section. -->
            <td class="row-header">
              <axsl:apply-templates select="fn" mode="id2282404"/>
            </td>
            <td class="row-header">
              <axsl:apply-templates select="email" mode="id2282426"/>
            </td>
          </tr></axsl:if>
          <axsl:if test="@item-type = 'card'"><tr>
            <td/>
            <td xml:space="preserve">
              <axsl:apply-templates select="url" mode="id2282454"/>
              <axsl:choose><axsl:when test="@item-value"><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value" select="@item-value"/><a href="{template:choice(/items/@filtered, '../')}../card/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:when><axsl:otherwise><axsl:variable name="this-name">item-value</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../card/{template:url-encode(template:url-encode($this-value))}/">(Edit)</a></axsl:otherwise></axsl:choose>
            </td>
            <td>
              <ul>
                <axsl:apply-templates select="tel" mode="id2282485"/>
              </ul>
            </td>
          </tr></axsl:if>
        </tbody>
  </axsl:template>
  <axsl:template match="organizer" mode="id2281815">
    <span xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
                <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><a href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
              </span>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2281847">
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
  <axsl:template match="summary" mode="id2281877">
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
  <axsl:template match="created" mode="id2281914">
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
  <axsl:template match="description" mode="id2281935">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2281967">
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
  <axsl:template match="summary" mode="id2281982">
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
  <axsl:template match="organizer" mode="id2282059">
    <span xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve">
                <axsl:choose><axsl:when test="@uri"><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value" select="@uri"/><a href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/"><axsl:value-of select="$this-value"/></a></axsl:when><axsl:otherwise><axsl:variable name="this-name">uri</axsl:variable><axsl:variable name="this-value"/><a href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/"><axsl:value-of select="$this-value"/></a></axsl:otherwise></axsl:choose>
              </span>
  </axsl:template>
  <axsl:template match="dtstart" mode="id2282089">
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
  <axsl:template match="dtend" mode="id2282104">
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
  <axsl:template match="summary" mode="id2282133">
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
  <axsl:template match="created" mode="id2282160">
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
  <axsl:template match="description" mode="id2282181">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="sender" mode="id2282258">
    <axsl:choose>
      <axsl:when test="@name">
        <axsl:variable name="this-name">name</axsl:variable>
        <axsl:variable name="this-value" select="@name"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode($this-value)}/">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">name</axsl:variable>
        <axsl:variable name="this-value"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode($this-value)}/">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="sender" mode="id2282279">
    <axsl:choose>
      <axsl:when test="@number">
        <axsl:variable name="this-name">number</axsl:variable>
        <axsl:variable name="this-value" select="@number"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">number</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="created" mode="id2282304">
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
  <axsl:template match="body" mode="id2282325">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <td xmlns="http://www.w3.org/1999/xhtml" class="message" colspan="2">
          <axsl:value-of select="$this-value"/>
        </td>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="fn" mode="id2282404">
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
  <axsl:template match="email" mode="id2282426">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}../person/{template:url-encode(template:url-encode($this-value))}/">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="url" mode="id2282454">
    <axsl:choose>
      <axsl:when test="@details">
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value" select="@details"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}{$this-value}">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">details</axsl:variable>
        <axsl:variable name="this-value"/>
        <a xmlns="http://www.w3.org/1999/xhtml" href="{template:choice(/items/@filtered, '../')}{$this-value}">
          <axsl:value-of select="$this-value"/>
        </a>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="tel" mode="id2282485">
    <li xmlns="http://www.w3.org/1999/xhtml">
                  <axsl:choose><axsl:when test="@type"><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value" select="@type"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">type</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>:
                  <axsl:choose><axsl:when test="@details"><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value" select="@details"/><span><axsl:value-of select="$this-value"/></span></axsl:when><axsl:otherwise><axsl:variable name="this-name">details</axsl:variable><axsl:variable name="this-value"/><span><axsl:value-of select="$this-value"/></span></axsl:otherwise></axsl:choose>
                </li>
  </axsl:template>
</axsl:stylesheet>
