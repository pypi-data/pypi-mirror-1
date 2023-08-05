<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="status"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2286351"/>
  </axsl:template>
  <axsl:template match="candidate" mode="id2286351">
    <candidate>
      <axsl:apply-templates select="@*"/>
      <identity>
        <axsl:apply-templates select="./identity/@*"/>
      </identity>
      <status>
        <axsl:apply-templates select="./status/@*"/>
        <axsl:for-each select="$status/status/status-enum">
          <axsl:copy>
            <axsl:apply-templates select="@*"/>
            <axsl:copy-of select="node()"/>
          </axsl:copy>
        </axsl:for-each>
      </status>
      <skills>
        <axsl:apply-templates select="./skills/@*"/>
        <axsl:apply-templates select="./skills/placeholder|./skills/skill" mode="id2286472"/>
      </skills>
      <qualifications>
        <axsl:apply-templates select="./qualifications/@*"/>
        <axsl:apply-templates select="./qualifications/placeholder|./qualifications/qualification" mode="id2286458"/>
      </qualifications>
      <experience>
        <axsl:apply-templates select="./experience/@*"/>
        <axsl:apply-templates select="./experience/placeholder|./experience/employment" mode="id2286512"/>
      </experience>
    </candidate>
  </axsl:template>
  <axsl:template match="skill" mode="id2286472">
    <skill>
      <axsl:apply-templates select="@*"/>
    </skill>
  </axsl:template>
  <axsl:template match="qualification" mode="id2286458">
    <qualification>
      <axsl:apply-templates select="@*"/>
    </qualification>
  </axsl:template>
  <axsl:template match="employment" mode="id2286512">
    <employment>
      <axsl:apply-templates select="@*"/>
    </employment>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286351">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286403">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286352">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286390">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286436">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286472">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286437">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286458">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286427">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286512">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
