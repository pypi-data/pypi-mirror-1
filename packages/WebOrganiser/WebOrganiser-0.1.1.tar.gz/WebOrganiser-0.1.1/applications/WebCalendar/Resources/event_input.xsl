<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2313083"/>
  </axsl:template>
  <axsl:template match="item" mode="id2313083">
    <item>
      <axsl:apply-templates select="@*"/>
      <event>
        <axsl:apply-templates select="./event/@*"/>
        <created>
          <axsl:apply-templates select="./event/created/@*"/>
        </created>
        <dtstamp>
          <axsl:apply-templates select="./event/dtstamp/@*"/>
        </dtstamp>
        <sequence>
          <axsl:apply-templates select="./event/sequence/@*"/>
        </sequence>
        <last-modified>
          <axsl:apply-templates select="./event/last-modified/@*"/>
        </last-modified>
        <class>
          <axsl:apply-templates select="./event/class/@*"/>
        </class>
        <priority>
          <axsl:apply-templates select="./event/priority/@*"/>
        </priority>
        <transp>
          <axsl:apply-templates select="./event/transp/@*"/>
        </transp>
        <summary>
          <axsl:apply-templates select="./event/summary/@*"/>
        </summary>
        <location>
          <axsl:apply-templates select="./event/location/@*"/>
        </location>
        <dtstart>
          <axsl:apply-templates select="./event/dtstart/@*"/>
          <axsl:apply-templates select="./event/dtstart/placeholder|./event/dtstart/month" mode="id2313289"/>
        </dtstart>
        <dtend>
          <axsl:apply-templates select="./event/dtend/@*"/>
          <axsl:apply-templates select="./event/dtend/placeholder|./event/dtend/month" mode="id2313379"/>
        </dtend>
        <organizer-search>
          <axsl:apply-templates select="./event/organizer-search/@*"/>
        </organizer-search>
        <organizer-suggestions>
          <axsl:apply-templates select="./event/organizer-suggestions/@*"/>
          <axsl:apply-templates select="./event/organizer-suggestions/placeholder|./event/organizer-suggestions/organizer-suggestion" mode="id2313206"/>
        </organizer-suggestions>
        <organizers>
          <axsl:apply-templates select="./event/organizers/@*"/>
          <axsl:apply-templates select="./event/organizers/placeholder|./event/organizers/organizer" mode="id2313472"/>
        </organizers>
        <attendee-search>
          <axsl:apply-templates select="./event/attendee-search/@*"/>
        </attendee-search>
        <attendee-suggestions>
          <axsl:apply-templates select="./event/attendee-suggestions/@*"/>
          <axsl:apply-templates select="./event/attendee-suggestions/placeholder|./event/attendee-suggestions/attendee-suggestion" mode="id2313388"/>
        </attendee-suggestions>
        <attendees>
          <axsl:apply-templates select="./event/attendees/@*"/>
          <axsl:apply-templates select="./event/attendees/placeholder|./event/attendees/attendee" mode="id2313247"/>
        </attendees>
      </event>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2313289">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2313359"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2313359">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2313428"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2313437"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2313428">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2313437">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="month" mode="id2313379">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2313400"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2313400">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2313464"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2313478"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2313464">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2313478">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer-suggestion" mode="id2313206">
    <organizer-suggestion>
      <axsl:apply-templates select="@*"/>
    </organizer-suggestion>
  </axsl:template>
  <axsl:template match="organizer" mode="id2313472">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee-suggestion" mode="id2313388">
    <attendee-suggestion>
      <axsl:apply-templates select="@*"/>
    </attendee-suggestion>
  </axsl:template>
  <axsl:template match="attendee" mode="id2313247">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313083">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313121">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313162">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313169">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313176">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313177">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313193">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313198">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313208">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313228">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313238">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313243">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313289">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313359">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313428">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313437">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313263">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313379">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313400">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313464">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313478">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313401">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313309">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313206">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313265">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313472">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313139">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313351">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313388">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313452">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2313247">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
