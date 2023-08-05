<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="category"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2343523"/>
  </axsl:template>
  <axsl:template match="package" mode="id2343523">
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
        <axsl:apply-templates select="./platforms/placeholder|./platforms/platform" mode="id2371536"/>
      </platforms>
      <supported-platforms>
        <axsl:apply-templates select="./supported-platforms/@*"/>
        <axsl:apply-templates select="./supported-platforms/placeholder|./supported-platforms/supported-platform" mode="id2376132"/>
      </supported-platforms>
      <keywords>
        <axsl:apply-templates select="./keywords/@*"/>
        <axsl:apply-templates select="./keywords/placeholder|./keywords/keyword" mode="id2367476"/>
      </keywords>
      <authors>
        <axsl:apply-templates select="./authors/@*"/>
        <axsl:apply-templates select="./authors/placeholder|./authors/author" mode="id2358635"/>
      </authors>
      <dependencies>
        <axsl:apply-templates select="./dependencies/@*"/>
        <axsl:apply-templates select="./dependencies/placeholder|./dependencies/dependency" mode="id2351841"/>
      </dependencies>
      <axsl:apply-templates select="./placeholder|./error" mode="id2376250"/>
    </package>
  </axsl:template>
  <axsl:template match="error" mode="id2376250">
    <error>
      <axsl:apply-templates select="@*"/>
    </error>
  </axsl:template>
  <axsl:template match="platform" mode="id2371536">
    <platform>
      <axsl:apply-templates select="@*"/>
    </platform>
  </axsl:template>
  <axsl:template match="supported-platform" mode="id2376132">
    <supported-platform>
      <axsl:apply-templates select="@*"/>
    </supported-platform>
  </axsl:template>
  <axsl:template match="keyword" mode="id2367476">
    <keyword>
      <axsl:apply-templates select="@*"/>
    </keyword>
  </axsl:template>
  <axsl:template match="author" mode="id2358635">
    <author>
      <axsl:apply-templates select="@*"/>
    </author>
  </axsl:template>
  <axsl:template match="dependency" mode="id2351841">
    <dependency>
      <axsl:apply-templates select="@*"/>
    </dependency>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2343523">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2376250">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2371848">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2371857">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2343250">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2376070">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2371536">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2335244">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2376132">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2376143">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2367476">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2376146">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2358635">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2367494">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2351841">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
