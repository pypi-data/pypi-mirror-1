<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2314583"/>
  </axsl:template>
  <axsl:template match="item" mode="id2314583">
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
          <axsl:apply-templates select="./journal/dtstart/placeholder|./journal/dtstart/month" mode="id2318701"/>
        </dtstart>
        <organizers>
          <axsl:apply-templates select="./journal/organizers/@*"/>
          <axsl:apply-templates select="./journal/organizers/placeholder|./journal/organizers/organizer" mode="id2318780"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./journal/attendees/@*"/>
          <axsl:apply-templates select="./journal/attendees/placeholder|./journal/attendees/attendee" mode="id2318814"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./journal/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./journal/person-suggestions/@*"/>
          <axsl:apply-templates select="./journal/person-suggestions/placeholder|./journal/person-suggestions/card" mode="id2310737"/>
        </person-suggestions>
      </journal>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2318701">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2318779"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2318779">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2318846"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2318857"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2318846">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2318857">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer" mode="id2318780">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2318814">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2310737">
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
  <axsl:template match="placeholder" mode="id2314583">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314621">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310638">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310645">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310652">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314652">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314635">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310668">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310698">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310688">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310700">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318701">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318779">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318846">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318857">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310665">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318780">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318746">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318814">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2314631">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310708">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2310737">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318870">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318882">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2318891">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
