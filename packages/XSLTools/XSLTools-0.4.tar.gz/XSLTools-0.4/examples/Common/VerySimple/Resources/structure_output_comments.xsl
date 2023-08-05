<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <axsl:apply-templates select="options" mode="id2279649"/>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="options" mode="id2279649">
    <p xmlns="http://www.w3.org/1999/xhtml" template:id="comment-node" id="{template:this-element()}">
    <axsl:apply-templates select="comment" mode="id2330955"/>
  </p>
  </axsl:template>
  <axsl:template match="comment" mode="id2330955">
    <span xmlns="http://www.w3.org/1999/xhtml">Comment:
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><textarea cols="40" rows="3" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><textarea cols="40" rows="3" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:otherwise></axsl:choose>
    </span>
  </axsl:template>
</axsl:stylesheet>
