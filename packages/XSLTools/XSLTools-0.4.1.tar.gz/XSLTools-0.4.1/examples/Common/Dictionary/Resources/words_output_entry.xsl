<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <axsl:apply-templates select="matches" mode="id2279580"/>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="matches" mode="id2279580">
    <p xmlns="http://www.w3.org/1999/xhtml" id="{template:this-element()}" template:id="matches-node">
    Matches:
    <axsl:choose><axsl:when test="@word"><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value" select="@word"/><select name="{template:this-attribute()}">
      <!-- onchange="requestUpdate(
        'word',
        '{template:new-attribute('word')}',
        '{template:other-elements(..)}',
        '{template:other-attributes('word', ..)}',
        '/words/entry')" -->
      <axsl:apply-templates select="match-enum" mode="id2306557"/>
    </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
      <!-- onchange="requestUpdate(
        'word',
        '{template:new-attribute('word')}',
        '{template:other-elements(..)}',
        '{template:other-attributes('word', ..)}',
        '/words/entry')" -->
      <axsl:apply-templates select="match-enum" mode="id2306557"/>
    </select></axsl:otherwise></axsl:choose>
  </p>
  </axsl:template>
  <axsl:template match="match-enum" mode="id2306557">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@word}">
      <axsl:if test="@word = ../@word">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@word"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
