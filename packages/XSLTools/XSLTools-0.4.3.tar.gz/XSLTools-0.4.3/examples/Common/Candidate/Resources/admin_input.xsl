<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2282158"/>
  </axsl:template>
  <axsl:template match="admin" mode="id2282158">
    <admin>
      <axsl:apply-templates select="@*"/>
      <cvs>
        <axsl:apply-templates select="./cvs/@*"/>
        <axsl:apply-templates select="./cvs/placeholder|./cvs/cv" mode="id2282244"/>
      </cvs>
    </admin>
  </axsl:template>
  <axsl:template match="cv" mode="id2282244">
    <cv>
      <axsl:apply-templates select="@*"/>
    </cv>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282158">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282208">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282244">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
