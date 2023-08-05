<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2304176"/>
  </axsl:template>
  <axsl:template match="recursive" mode="id2304176">
    <recursive>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./list" mode="id2284233"/>
    </recursive>
  </axsl:template>
  <axsl:template match="list" mode="id2284233">
    <list>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./item" mode="id2275995"/>
    </list>
  </axsl:template>
  <axsl:template match="item" mode="id2275995">
    <item>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="list" mode="id2284233"/>
    </item>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2304176">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2284233">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2275995">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
