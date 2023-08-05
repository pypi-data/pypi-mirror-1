<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="category"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2316785"/>
  </axsl:template>
  <axsl:template match="package" mode="id2316785">
    <package>
      <axsl:apply-templates select="@*"/>
      <categories>
        <axsl:apply-templates select="./categories/@*"/>
        <category>
          <axsl:apply-templates select="./categories/category/@*"/>
          <axsl:variable name="values-category-enum" select="./categories/category/category-enum/@value"/>
          <axsl:for-each select="$category/category/category-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:if test="$values-category-enum[string() = current()/@value]">
                <axsl:attribute name="value-is-set">true</axsl:attribute>
              </axsl:if>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </category>
      </categories>
      <platforms>
        <axsl:apply-templates select="./platforms/@*"/>
        <axsl:apply-templates select="./platforms/placeholder|./platforms/platform" mode="id2323990"/>
      </platforms>
      <supported-platforms>
        <axsl:apply-templates select="./supported-platforms/@*"/>
        <axsl:apply-templates select="./supported-platforms/placeholder|./supported-platforms/supported-platform" mode="id2324010"/>
      </supported-platforms>
      <keywords>
        <axsl:apply-templates select="./keywords/@*"/>
        <axsl:apply-templates select="./keywords/placeholder|./keywords/keyword" mode="id2324030"/>
      </keywords>
      <authors>
        <axsl:apply-templates select="./authors/@*"/>
        <axsl:apply-templates select="./authors/placeholder|./authors/author" mode="id2324116"/>
      </authors>
      <dependencies>
        <axsl:apply-templates select="./dependencies/@*"/>
        <axsl:apply-templates select="./dependencies/placeholder|./dependencies/dependency" mode="id2324145"/>
      </dependencies>
      <axsl:apply-templates select="./placeholder|./error" mode="id2312836"/>
    </package>
  </axsl:template>
  <axsl:template match="error" mode="id2312836">
    <error>
      <axsl:apply-templates select="@*"/>
    </error>
  </axsl:template>
  <axsl:template match="platform" mode="id2323990">
    <platform>
      <axsl:apply-templates select="@*"/>
    </platform>
  </axsl:template>
  <axsl:template match="supported-platform" mode="id2324010">
    <supported-platform>
      <axsl:apply-templates select="@*"/>
    </supported-platform>
  </axsl:template>
  <axsl:template match="keyword" mode="id2324030">
    <keyword>
      <axsl:apply-templates select="@*"/>
    </keyword>
  </axsl:template>
  <axsl:template match="author" mode="id2324116">
    <author>
      <axsl:apply-templates select="@*"/>
    </author>
  </axsl:template>
  <axsl:template match="dependency" mode="id2324145">
    <dependency>
      <axsl:apply-templates select="@*"/>
    </dependency>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2316785">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312836">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312856">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312858">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312871">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2312878">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323990">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2323999">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324010">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324020">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324030">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324027">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324116">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324133">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2324145">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
