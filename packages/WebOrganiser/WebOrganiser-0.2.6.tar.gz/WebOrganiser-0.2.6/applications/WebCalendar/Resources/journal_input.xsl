<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2300989"/>
  </axsl:template>
  <axsl:template match="item" mode="id2300989">
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
          <axsl:apply-templates select="./journal/dtstart/placeholder|./journal/dtstart/month" mode="id2317384"/>
        </dtstart>
        <organizers>
          <axsl:apply-templates select="./journal/organizers/@*"/>
          <axsl:apply-templates select="./journal/organizers/placeholder|./journal/organizers/organizer" mode="id2318713"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./journal/attendees/@*"/>
          <axsl:apply-templates select="./journal/attendees/placeholder|./journal/attendees/attendee" mode="id2318700"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./journal/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./journal/person-suggestions/@*"/>
          <axsl:apply-templates select="./journal/person-suggestions/placeholder|./journal/person-suggestions/card" mode="id2318720"/>
        </person-suggestions>
      </journal>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2317384">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2318681"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2318681">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2318750"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2318738"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2318750">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2318738">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer" mode="id2318713">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2318700">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2318720">
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
  <axsl:template match="placeholder" mode="id2300989">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310132">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301366">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301374">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301380">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310159">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310146">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301396">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300902">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301413">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300905">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2317384">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318681">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318750">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318738">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310144">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318713">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2301377">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318700">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318728">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300897">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318720">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2322945">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2322956">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2322965">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
