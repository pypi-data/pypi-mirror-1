<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="status"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2286100"/>
  </axsl:template>
  <axsl:template match="candidate" mode="id2286100">
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
        <axsl:apply-templates select="./skills/placeholder|./skills/skill" mode="id2286221"/>
      </skills>
      <qualifications>
        <axsl:apply-templates select="./qualifications/@*"/>
        <axsl:apply-templates select="./qualifications/placeholder|./qualifications/qualification" mode="id2286235"/>
      </qualifications>
      <experience>
        <axsl:apply-templates select="./experience/@*"/>
        <axsl:apply-templates select="./experience/placeholder|./experience/employment" mode="id2286261"/>
      </experience>
    </candidate>
  </axsl:template>
  <axsl:template match="skill" mode="id2286221">
    <skill>
      <axsl:apply-templates select="@*"/>
    </skill>
  </axsl:template>
  <axsl:template match="qualification" mode="id2286235">
    <qualification>
      <axsl:apply-templates select="@*"/>
    </qualification>
  </axsl:template>
  <axsl:template match="employment" mode="id2286261">
    <employment>
      <axsl:apply-templates select="@*"/>
    </employment>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286100">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286151">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286101">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286139">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286184">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286221">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286189">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286235">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286187">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286261">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
