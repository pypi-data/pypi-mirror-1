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
    <axsl:apply-templates select="*" mode="id2327835"/>
  </axsl:template>
  <axsl:template match="item" mode="id2327835">
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
          <axsl:apply-templates select="./event/dtstart/placeholder|./event/dtstart/month" mode="id2328055"/>
        </dtstart>
        <dtend>
          <axsl:apply-templates select="./event/dtend/@*"/>
          <axsl:apply-templates select="./event/dtend/placeholder|./event/dtend/month" mode="id2327949"/>
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
          <axsl:apply-templates select="./event/organizers/placeholder|./event/organizers/organizer" mode="id2328289"/>
        </organizers>
        <attendees>
          <axsl:apply-templates select="./event/attendees/@*"/>
          <axsl:apply-templates select="./event/attendees/placeholder|./event/attendees/attendee" mode="id2328325"/>
        </attendees>
        <person-search>
          <axsl:apply-templates select="./event/person-search/@*"/>
        </person-search>
        <person-suggestions>
          <axsl:apply-templates select="./event/person-suggestions/@*"/>
          <axsl:apply-templates select="./event/person-suggestions/placeholder|./event/person-suggestions/card" mode="id2328368"/>
        </person-suggestions>
      </event>
    </item>
  </axsl:template>
  <axsl:template match="month" mode="id2328055">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2328132"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2328132">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2328200"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2328209"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2328200">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2328209">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="month" mode="id2327949">
    <month>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./week" mode="id2328038"/>
    </month>
  </axsl:template>
  <axsl:template match="week" mode="id2328038">
    <week>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2328244"/>
      <axsl:apply-templates select="./placeholder|./day" mode="id2328253"/>
    </week>
  </axsl:template>
  <axsl:template match="day" mode="id2328244">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="day" mode="id2328253">
    <day>
      <axsl:apply-templates select="@*"/>
    </day>
  </axsl:template>
  <axsl:template match="organizer" mode="id2328289">
    <organizer>
      <axsl:apply-templates select="@*"/>
    </organizer>
  </axsl:template>
  <axsl:template match="attendee" mode="id2328325">
    <attendee>
      <axsl:apply-templates select="@*"/>
    </attendee>
  </axsl:template>
  <axsl:template match="card" mode="id2328368">
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
  <axsl:template match="placeholder" mode="id2327835">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327873">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327914">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327923">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327930">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327937">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327944">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327952">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327958">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327965">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327987">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327996">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328002">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327994">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328055">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328132">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328200">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328209">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328052">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327949">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328038">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328244">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328253">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328041">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328097">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328004">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327951">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328130">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327915">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328031">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328073">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328106">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328216">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328010">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328228">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327942">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328190">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328208">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328289">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2327918">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328325">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328319">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328353">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328368">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328426">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328438">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328450">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
