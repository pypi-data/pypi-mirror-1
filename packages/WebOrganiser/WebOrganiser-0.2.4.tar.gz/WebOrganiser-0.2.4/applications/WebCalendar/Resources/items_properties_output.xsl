<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:apply-templates select="items" mode="id2286823"/>
  </axsl:template>
  <axsl:template match="items" mode="id2286823">
    <axsl:apply-templates select="table" mode="id2286823"/>
  </axsl:template>
  <axsl:template match="table" mode="id2286823">
    <D:multistatus xmlns:D="DAV:">

  <!-- Collections are generated only for non-leaf, non-collection-export resources. -->

  <axsl:if test="not(/items/@leaf = 'yes')"><D:response>
    <D:href><axsl:value-of select="$path"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>2005-01-01T00:00:00Z</D:creationdate>
        <D:displayname><axsl:value-of select="$path"/></D:displayname>
        <D:resourcetype>
          <D:collection/>
        </D:resourcetype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response></axsl:if>

  <!-- Collection exports are described by a simple template. -->

  <axsl:if test="/items/@collection-export = 'yes'"><D:response>
    <D:href><axsl:value-of select="$path"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>2005-01-01T00:00:00Z</D:creationdate>
        <D:displayname><axsl:value-of select="$path"/></D:displayname>
        <D:resourcetype>
        </D:resourcetype>
        <D:getcontenttype>text/calendar</D:getcontenttype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response></axsl:if>

  <!-- Items, whether in a collection or as leaf resources are fully described. -->

  <axsl:apply-templates select="item" mode="id2286945"/>
</D:multistatus>
  </axsl:template>
  <axsl:template match="item" mode="id2286945">
    <D:response xmlns:D="DAV:">
    <axsl:if test="not(/items/@leaf = 'yes')"><D:href><axsl:value-of select="concat($path, template:url-encode(template:url-encode(@item-value)))"/></D:href></axsl:if>
    <axsl:if test="/items/@leaf = 'yes'"><D:href><axsl:value-of select="$path"/></D:href></axsl:if>
    <D:propstat>
      <D:prop>
        <axsl:if test="created/@datetime != ''"><D:creationdate><axsl:value-of select="concat(substring(created/@datetime, 1, 4), '-', substring(created/@datetime, 5, 2), '-', substring(created/@datetime, 7, 2), 'T', substring(created/@datetime, 10, 2), ':', substring(created/@datetime, 12, 2), ':', substring(created/@datetime, 14, 2), 'Z', substring(created/@datetime, 17))"/></D:creationdate></axsl:if>
        <axsl:if test="@item-type = 'calendar'"><D:displayname><axsl:value-of select="@name"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'event'"><D:displayname><axsl:value-of select="summary/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'to-do'"><D:displayname><axsl:value-of select="summary/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'card'"><D:displayname><axsl:value-of select="fn/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'journal'"><D:displayname><axsl:value-of select="summary/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'message'"><D:displayname><axsl:value-of select="body/@details"/></D:displayname></axsl:if>
        <D:resourcetype>
          <axsl:if test="/items/@items-are-containers = 'yes'"><D:collection/></axsl:if>
        </D:resourcetype>
        <axsl:if test="not(/items/@items-are-containers = 'yes') and @item-type = 'calendar'"><D:getcontenttype>text/calendar</D:getcontenttype></axsl:if>
        <axsl:if test="not(/items/@items-are-containers = 'yes') and @item-type = 'event'"><D:getcontenttype>text/calendar</D:getcontenttype></axsl:if>
        <axsl:if test="not(/items/@items-are-containers = 'yes') and @item-type = 'to-do'"><D:getcontenttype>text/calendar</D:getcontenttype></axsl:if>
        <axsl:if test="not(/items/@items-are-containers = 'yes') and @item-type = 'card'"><D:getcontenttype>text/x-vcard</D:getcontenttype></axsl:if>
        <axsl:if test="not(/items/@items-are-containers = 'yes') and @item-type = 'message'"><D:getcontenttype>text/plain</D:getcontenttype></axsl:if>
        <axsl:if test="not(/items/@items-are-containers = 'yes')"><D:getcontentlength>0</D:getcontentlength></axsl:if>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
  </axsl:template>
</axsl:stylesheet>
