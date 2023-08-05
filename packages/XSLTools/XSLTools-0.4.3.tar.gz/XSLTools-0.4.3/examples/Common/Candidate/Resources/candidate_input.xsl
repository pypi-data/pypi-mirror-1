<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="status"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2285934"/>
  </axsl:template>
  <axsl:template match="candidate" mode="id2285934">
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
        <axsl:apply-templates select="./skills/placeholder|./skills/skill" mode="id2286055"/>
      </skills>
      <qualifications>
        <axsl:apply-templates select="./qualifications/@*"/>
        <axsl:apply-templates select="./qualifications/placeholder|./qualifications/qualification" mode="id2286041"/>
      </qualifications>
      <experience>
        <axsl:apply-templates select="./experience/@*"/>
        <axsl:apply-templates select="./experience/placeholder|./experience/employment" mode="id2286095"/>
      </experience>
    </candidate>
  </axsl:template>
  <axsl:template match="skill" mode="id2286055">
    <skill>
      <axsl:apply-templates select="@*"/>
    </skill>
  </axsl:template>
  <axsl:template match="qualification" mode="id2286041">
    <qualification>
      <axsl:apply-templates select="@*"/>
    </qualification>
  </axsl:template>
  <axsl:template match="employment" mode="id2286095">
    <employment>
      <axsl:apply-templates select="@*"/>
    </employment>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2285934">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2285986">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2285935">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2285973">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286018">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286055">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286020">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286041">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286009">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286095">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
