<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <tbody xmlns="http://www.w3.org/1999/xhtml" template:id="platforms" id="platforms">
      <axsl:apply-templates select="platforms" mode="id2316858"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add platform!" onclick=" return requestUpdateArea(   'platforms',   '{template:other-attributes('name', .)},{template:selector-name('add_platform', .)}',   'platforms',   '{template:other-elements(platforms)}',   '/package') " name="add_platform={template:this-element()}"/></td>
      </tr>
    </tbody>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="platforms" mode="id2316858">
    <axsl:apply-templates select="platform" mode="id2316858"/>
  </axsl:template>
  <axsl:template match="platform" mode="id2316858">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Platform name</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          <input type="submit" value="Remove!" onclick=" return requestUpdateArea(   'platforms',   '{template:selector-name('remove_platform', .)}',   'platforms',   '{template:other-elements(..)}',   '/package') " name="remove_platform={template:this-element()}"/></td>
      </tr>
  </axsl:template>
</axsl:stylesheet>
