<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="type"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2328512"/>
  </axsl:template>
  <axsl:template match="structure" mode="id2328512">
    <structure>
      <axsl:apply-templates select="@*"/>
      <axsl:apply-templates select="./placeholder|./item" mode="id2277729"/>
    </structure>
  </axsl:template>
  <axsl:template match="item" mode="id2277729">
    <item>
      <axsl:apply-templates select="@*"/>
      <type>
        <axsl:apply-templates select="./type/@*"/>
        <axsl:variable name="values-type-enum" select="./type/type-enum/@value"/>
        <axsl:for-each select="$type/type/type-enum">
          <axsl:copy>
            <axsl:apply-templates select="@*"/>
            <axsl:if test="$values-type-enum[string() = current()/@value]">
              <axsl:attribute name="value-is-set">true</axsl:attribute>
            </axsl:if>
            <axsl:copy-of select="node()"/>
          </axsl:copy>
        </axsl:for-each>
      </type>
      <options>
        <axsl:apply-templates select="./options/@*"/>
        <comment>
          <axsl:apply-templates select="./options/comment/@*"/>
        </comment>
      </options>
      <axsl:apply-templates select="./placeholder|./subitem" mode="id2329466"/>
    </item>
  </axsl:template>
  <axsl:template match="subitem" mode="id2329466">
    <subitem>
      <axsl:apply-templates select="@*"/>
    </subitem>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328512">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277729">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2328718">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2330837">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2332243">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2332267">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2329466">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
