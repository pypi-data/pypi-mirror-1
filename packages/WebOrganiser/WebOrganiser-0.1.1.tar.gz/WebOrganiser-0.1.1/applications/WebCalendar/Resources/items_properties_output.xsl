<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:apply-templates select="items" mode="id2287656"/>
  </axsl:template>
  <axsl:template match="items" mode="id2287656">
    <axsl:apply-templates select="table" mode="id2287656"/>
  </axsl:template>
  <axsl:template match="table" mode="id2287656">
    <D:multistatus xmlns:D="DAV:">
  <axsl:if test="not(/items/@leaf = 'yes')"><D:response>
    <D:href><axsl:value-of select="$path"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>20050101</D:creationdate>
        <D:displayname><axsl:value-of select="$path"/></D:displayname>
        <D:resourcetype>
          <D:collection/>
        </D:resourcetype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response></axsl:if>
  <axsl:apply-templates select="item" mode="id2287727"/>
</D:multistatus>
  </axsl:template>
  <axsl:template match="item" mode="id2287727">
    <D:response xmlns:D="DAV:">
    <axsl:if test="not(/items/@filter-type = 'person') or /items/@person"><D:href><axsl:value-of select="concat($path, template:url-encode(template:url-encode(@item-value)))"/></D:href></axsl:if>
    <axsl:if test="/items/@filter-type = 'person' and not(/items/@person)"><D:href><axsl:value-of select="concat($path, template:url-encode(template:url-encode(email/@details)))"/></D:href></axsl:if>
    <D:propstat>
      <D:prop>
        <D:creationdate><axsl:value-of select="created/@datetime"/></D:creationdate>
        <axsl:if test="@item-type = 'calendar'"><D:displayname><axsl:value-of select="@name"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'event'"><D:displayname><axsl:value-of select="summary/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'to-do'"><D:displayname><axsl:value-of select="summary/@details"/></D:displayname></axsl:if>
        <axsl:if test="@item-type = 'card'"><D:displayname><axsl:value-of select="fn/@details"/></D:displayname></axsl:if>
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
