<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2318223"/>
  </axsl:template>
  <axsl:template match="item" mode="id2318223">
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
          <axsl:apply-templates select="./to-do/organizers/placeholder|./to-do/organizers/organizer" mode="id2324781"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./to-do/attendees/@*"/>
          <axsl:apply-templates select="./to-do/attendees/placeholder|./to-do/attendees/attendee" mode="id2324824"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./to-do/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./to-do/person-suggestions/@*"/>
          <axsl:apply-templates select="./to-do/person-suggestions/placeholder|./to-do/person-suggestions/card" mode="id2324865"/>
        </person-suggestions>
      </to-do>
    </item>
  </axsl:template>
  <axsl:template match="organizer" mode="id2324781">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2324824">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2324865">
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
  <axsl:template match="placeholder" mode="id2318223">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2274995">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277976">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277983">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277991">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277998">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278003">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278007">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278022">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324722">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324732">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324741">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324748">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324720">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324781">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324754">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324824">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324742">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324842">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324865">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324923">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324935">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324946">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
