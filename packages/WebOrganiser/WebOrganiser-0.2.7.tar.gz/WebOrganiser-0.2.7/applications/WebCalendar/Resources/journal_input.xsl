<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2288043"/>
  </axsl:template>
  <axsl:template match="item" mode="id2288043">
    <item>
      <axsl:apply-templates select="@*"/>
      <journal>
        <axsl:apply-templates select="./journal/@*"/>
        <created>
          <axsl:apply-templates select="./journal/created/@*"/>
        </created>
        <dtstamp>
          <axsl:apply-templates select="./journal/dtstamp/@*"/>
        </dtstamp>
        <sequence>
          <axsl:apply-templates select="./journal/sequence/@*"/>
        </sequence>
        <last-modified>
          <axsl:apply-templates select="./journal/last-modified/@*"/>
        </last-modified>
        <class>
          <axsl:apply-templates select="./journal/class/@*"/>
        </class>
        <related-to>
          <axsl:apply-templates select="./journal/related-to/@*"/>
        </related-to>
        <summary>
          <axsl:apply-templates select="./journal/summary/@*"/>
        </summary>
        <description>
          <axsl:apply-templates select="./journal/description/@*"/>
        </description>
        <dtstart>
          <axsl:apply-templates select="./journal/dtstart/@*"/>
          <axsl:apply-templates select="./journal/dtstart/placeholder|./journal/dtstart/month" mode="id2321476"/>
        </dtstart>
        <organizers>
          <axsl:apply-templates select="./journal/organizers/@*"/>
          <axsl:apply-templates select="./journal/organizers/placeholder|./journal/organizers/organizer" mode="id2277279"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./journal/attendees/@*"/>
          <axsl:apply-templates select="./journal/attendees/placeholder|./journal/attendees/attendee" mode="id2280245"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./journal/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./journal/person-suggestions/@*"/>
          <axsl:apply-templates select="./journal/person-suggestions/placeholder|./journal/person-suggestions/card" mode="id2291134"/>
        </person-suggestions>
      </journal>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2321476">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2309401"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2309401">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2280216"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2280242"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2280216">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2280242">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer" mode="id2277279">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2280245">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2291134">
    <card>
      <axsl:apply-templates select="@*"/>
      <fn>
        <axsl:apply-templates select="./fn/@*"/>
      </fn>
      <email>
        <axsl:apply-templates select="./email/@*"/>
      </email>
      <uid>
        <axsl:apply-templates select="./uid/@*"/>
      </uid>
    </card>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2288043">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2291999">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277327">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277340">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277628">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277339">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298198">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298206">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298214">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277263">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277312">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2321476">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2309401">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2280216">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2280242">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277281">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277279">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2309404">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2280245">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277631">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277283">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2291134">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2281197">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2281215">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278255">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
