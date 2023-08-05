<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2293477"/>
  </axsl:template>
  <axsl:template match="item" mode="id2293477">
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
          <axsl:apply-templates select="./to-do/organizers/placeholder|./to-do/organizers/organizer" mode="id2320704"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./to-do/attendees/@*"/>
          <axsl:apply-templates select="./to-do/attendees/placeholder|./to-do/attendees/attendee" mode="id2320743"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./to-do/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./to-do/person-suggestions/@*"/>
          <axsl:apply-templates select="./to-do/person-suggestions/placeholder|./to-do/person-suggestions/card" mode="id2320788"/>
        </person-suggestions>
      </to-do>
    </item>
  </axsl:template>
  <axsl:template match="organizer" mode="id2320704">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2320743">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2320788">
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
  <axsl:template match="placeholder" mode="id2293477">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298463">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314167">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298482">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314185">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298472">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314196">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314204">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314213">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320645">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320652">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320660">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320668">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320640">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320704">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320674">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320743">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314211">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320653">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320788">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320846">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320857">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2320869">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
