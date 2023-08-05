<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2296628"/>
  </axsl:template>
  <axsl:template match="item" mode="id2296628">
    <item>
      <axsl:apply-templates select="@*"/>
      <to-do>
        <axsl:apply-templates select="./to-do/@*"/>
        <created>
          <axsl:apply-templates select="./to-do/created/@*"/>
        </created>
        <dtstamp>
          <axsl:apply-templates select="./to-do/dtstamp/@*"/>
        </dtstamp>
        <sequence>
          <axsl:apply-templates select="./to-do/sequence/@*"/>
        </sequence>
        <last-modified>
          <axsl:apply-templates select="./to-do/last-modified/@*"/>
        </last-modified>
        <class>
          <axsl:apply-templates select="./to-do/class/@*"/>
        </class>
        <priority>
          <axsl:apply-templates select="./to-do/priority/@*"/>
        </priority>
        <related-to>
          <axsl:apply-templates select="./to-do/related-to/@*"/>
        </related-to>
        <summary>
          <axsl:apply-templates select="./to-do/summary/@*"/>
        </summary>
        <description>
          <axsl:apply-templates select="./to-do/description/@*"/>
        </description>
        <percent-complete>
          <axsl:apply-templates select="./to-do/percent-complete/@*"/>
        </percent-complete>
        <location>
          <axsl:apply-templates select="./to-do/location/@*"/>
        </location>
        <organizers>
          <axsl:apply-templates select="./to-do/organizers/@*"/>
          <axsl:apply-templates select="./to-do/organizers/placeholder|./to-do/organizers/organizer" mode="id2324629"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./to-do/attendees/@*"/>
          <axsl:apply-templates select="./to-do/attendees/placeholder|./to-do/attendees/attendee" mode="id2324671"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./to-do/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./to-do/person-suggestions/@*"/>
          <axsl:apply-templates select="./to-do/person-suggestions/placeholder|./to-do/person-suggestions/card" mode="id2324713"/>
        </person-suggestions>
      </to-do>
    </item>
  </axsl:template>
  <axsl:template match="organizer" mode="id2324629">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2324671">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2324713">
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
  <axsl:template match="placeholder" mode="id2296628">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2274622">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324505">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324514">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324520">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324528">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324535">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324543">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324551">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324571">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324578">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324586">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324562">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324556">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324629">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324610">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324671">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324663">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324572">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324713">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324771">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324782">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324795">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
