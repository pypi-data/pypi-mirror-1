<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="hour"/>
  <axsl:param name="minute"/>
  <axsl:param name="second"/>
  <axsl:param name="hour"/>
  <axsl:param name="minute"/>
  <axsl:param name="second"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2335797"/>
  </axsl:template>
  <axsl:template match="item" mode="id2335797">
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
        <related-to>
          <axsl:apply-templates select="./event/related-to/@*"/>
        </related-to>
        <summary>
          <axsl:apply-templates select="./event/summary/@*"/>
        </summary>
        <location>
          <axsl:apply-templates select="./event/location/@*"/>
        </location>
        <description>
          <axsl:apply-templates select="./event/description/@*"/>
        </description>
        <dtstart>
          <axsl:apply-templates select="./event/dtstart/@*"/>
          <axsl:apply-templates select="./event/dtstart/placeholder|./event/dtstart/month" mode="id2336092"/>
        </dtstart>
        <dtend>
          <axsl:apply-templates select="./event/dtend/@*"/>
          <axsl:apply-templates select="./event/dtend/placeholder|./event/dtend/month" mode="id2336122"/>
        </dtend>
        <dtstart-time>
          <axsl:apply-templates select="./event/dtstart-time/@*"/>
          <hour>
            <axsl:apply-templates select="./event/dtstart-time/hour/@*"/>
            <axsl:for-each select="$hour/hour/hour-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </hour>
          <minute>
            <axsl:apply-templates select="./event/dtstart-time/minute/@*"/>
            <axsl:for-each select="$minute/minute/minute-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </minute>
          <second>
            <axsl:apply-templates select="./event/dtstart-time/second/@*"/>
            <axsl:for-each select="$second/second/second-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </second>
        </dtstart-time>
        <dtend-time>
          <axsl:apply-templates select="./event/dtend-time/@*"/>
          <hour>
            <axsl:apply-templates select="./event/dtend-time/hour/@*"/>
            <axsl:for-each select="$hour/hour/hour-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </hour>
          <minute>
            <axsl:apply-templates select="./event/dtend-time/minute/@*"/>
            <axsl:for-each select="$minute/minute/minute-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </minute>
          <second>
            <axsl:apply-templates select="./event/dtend-time/second/@*"/>
            <axsl:for-each select="$second/second/second-enum">
              <axsl:copy>
                <axsl:apply-templates select="@*"/>
                <axsl:copy-of select="node()"/>
              </axsl:copy>
            </axsl:for-each>
          </second>
        </dtend-time>
        <organizers>
          <axsl:apply-templates select="./event/organizers/@*"/>
          <axsl:apply-templates select="./event/organizers/placeholder|./event/organizers/organizer" mode="id2336382"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./event/attendees/@*"/>
          <axsl:apply-templates select="./event/attendees/placeholder|./event/attendees/attendee" mode="id2336428"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./event/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./event/person-suggestions/@*"/>
          <axsl:apply-templates select="./event/person-suggestions/placeholder|./event/person-suggestions/card" mode="id2336476"/>
        </person-suggestions>
      </event>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2336092">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2336147"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2336147">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2336228"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2336251"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2336228">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2336251">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="month" mode="id2336122">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2336185"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2336185">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2336287"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2336307"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2336287">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2336307">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer" mode="id2336382">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2336428">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2336476">
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
  <axsl:template match="placeholder" mode="id2335797">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335851">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335918">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335930">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335945">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335929">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335967">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335977">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335987">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335954">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336009">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336020">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336031">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335996">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336092">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336147">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336228">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336251">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335983">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336122">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336185">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336287">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336307">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336134">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336256">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336292">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336272">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336193">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335912">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336269">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336278">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336223">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336324">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336336">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336345">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336350">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336364">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335926">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336382">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336046">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336428">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335950">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336425">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336476">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336513">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336531">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2336549">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
