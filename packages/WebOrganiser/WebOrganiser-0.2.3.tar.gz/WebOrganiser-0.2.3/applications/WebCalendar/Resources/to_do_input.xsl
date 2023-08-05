<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2290251"/>
  </axsl:template>
  <axsl:template match="item" mode="id2290251">
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
          <axsl:apply-templates select="./to-do/organizers/placeholder|./to-do/organizers/organizer" mode="id2320707"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./to-do/attendees/@*"/>
          <axsl:apply-templates select="./to-do/attendees/placeholder|./to-do/attendees/attendee" mode="id2320749"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./to-do/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./to-do/person-suggestions/@*"/>
          <axsl:apply-templates select="./to-do/person-suggestions/placeholder|./to-do/person-suggestions/card" mode="id2320791"/>
        </person-suggestions>
      </to-do>
    </item>
  </axsl:template>
  <axsl:template match="organizer" mode="id2320707">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2320749">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2320791">
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
  <axsl:template match="placeholder" mode="id2290251">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2288376">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314234">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314244">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314251">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314259">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314263">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314256">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314276">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320650">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320658">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320667">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320674">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320663">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320707">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314267">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320749">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320756">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320672">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320791">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320848">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320860">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320871">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
