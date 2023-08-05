<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <div xmlns="http://www.w3.org/1999/xhtml" template:id="memory-node" id="{template:this-element()}">
      <axsl:apply-templates select="memory-unit" mode="id2300996"/>

      <p>
        <input type="submit" value="{template:i18n('Add memory')}" name="add-memory-unit={template:this-element()}"/>
      </p>
    </div>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="memory-unit" mode="id2300996">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Memory unit']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:otherwise>Memory unit</axsl:otherwise></axsl:choose></span>
        <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="memory-unit-enum" mode="id2301039"/>
        </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="memory-unit-enum" mode="id2301039"/>
        </select></axsl:otherwise></axsl:choose>
   
        <input type="submit" value="{template:i18n('Remove')}" name="remove-memory-unit={template:this-element()}"/>
      </p>
  </axsl:template>
  <axsl:template match="memory-unit-enum" mode="id2301039">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
