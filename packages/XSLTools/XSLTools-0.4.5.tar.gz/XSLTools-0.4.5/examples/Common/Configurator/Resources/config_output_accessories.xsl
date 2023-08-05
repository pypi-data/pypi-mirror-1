<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <axsl:apply-templates select="accessories" mode="id2295697"/>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="accessories" mode="id2295697">
    <div xmlns="http://www.w3.org/1999/xhtml" template:id="accessories-node" id="{template:this-element()}" class="accessories">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Accessories']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Accessories']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Accessories</axsl:otherwise></axsl:choose></h2>

    <select multiple="multiple" name="{template:list-attribute('accessory-enum',&#10;            'value')}">
      <axsl:apply-templates select="accessory-enum" mode="id2295749"/>
    </select>
  </div>
  </axsl:template>
  <axsl:template match="accessory-enum" mode="id2295749">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value-is-set">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
