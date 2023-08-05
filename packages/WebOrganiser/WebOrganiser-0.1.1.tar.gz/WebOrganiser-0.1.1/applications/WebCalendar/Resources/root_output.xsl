<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:apply-templates select="root" mode="id2312801"/>
  </axsl:template>
  <axsl:template match="root" mode="id2312801">
    <D:multistatus xmlns:D="DAV:">
  <D:response>
    <D:href><axsl:value-of select="$path"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>20050101</D:creationdate>
        <D:displayname>/</D:displayname>
        <D:resourcetype>
          <D:collection/>
        </D:resourcetype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
  <axsl:apply-templates select="directory" mode="id2274616"/>
  <axsl:apply-templates select="file" mode="id2312798"/>
</D:multistatus>
  </axsl:template>
  <axsl:template match="directory" mode="id2274616">
    <D:response xmlns:D="DAV:">
    <D:href><axsl:value-of select="concat($path, '/', @name)"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>20050101</D:creationdate>
        <D:displayname><axsl:value-of select="@name"/></D:displayname>
        <D:resourcetype>
          <D:collection/>
        </D:resourcetype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
  </axsl:template>
  <axsl:template match="file" mode="id2312798">
    <D:response xmlns:D="DAV:">
    <D:href><axsl:value-of select="concat($path, '/', @name)"/></D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>20050101</D:creationdate>
        <D:displayname><axsl:value-of select="@name"/></D:displayname>
        <D:resourcetype>
        </D:resourcetype>
      </D:prop>
      <D:getcontenttype>text/calendar</D:getcontenttype>
      <D:getcontentlength>0</D:getcontentlength>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
  </axsl:template>
</axsl:stylesheet>
