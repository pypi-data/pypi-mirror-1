<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2288986"/>
  </axsl:template>
  <axsl:template match="item" mode="id2288986">
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
          <axsl:apply-templates select="./to-do/organizers/placeholder|./to-do/organizers/organizer" mode="id2318528"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./to-do/attendees/@*"/>
          <axsl:apply-templates select="./to-do/attendees/placeholder|./to-do/attendees/attendee" mode="id2318526"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./to-do/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./to-do/person-suggestions/@*"/>
          <axsl:apply-templates select="./to-do/person-suggestions/placeholder|./to-do/person-suggestions/card" mode="id2318609"/>
        </person-suggestions>
      </to-do>
    </item>
  </axsl:template>
  <axsl:template match="organizer" mode="id2318528">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2318526">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2318609">
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
  <axsl:template match="placeholder" mode="id2288986">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2288065">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2311983">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2311991">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2311999">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2288071">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312014">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312021">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312028">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318467">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318474">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318480">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318489">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318462">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318528">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318560">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318526">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2311985">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318455">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318609">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318666">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318677">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318688">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
