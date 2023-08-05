<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <tbody xmlns="http://www.w3.org/1999/xhtml" template:id="keywords" id="keywords">
      <tr>
        <th colspan="2" class="heading">Keywords</th>
      </tr>
      <axsl:apply-templates select="keywords" mode="id2317390"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add keyword!" onclick=" return requestUpdateArea(   'keywords',   '{template:other-attributes('name', .)},{template:selector-name('add_keyword', .)}',   'keywords',   '{template:other-elements(keywords)}',   '/package') " name="add_keyword={template:this-element()}"/></td>
      </tr>
    </tbody>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="keywords" mode="id2317390">
    <axsl:apply-templates select="keyword" mode="id2317390"/>
  </axsl:template>
  <axsl:template match="keyword" mode="id2317390">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Keyword</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          <input type="submit" value="Remove!" onclick=" return requestUpdateArea(   'keywords',   '{template:selector-name('remove_keyword', .)}',   'keywords',   '{template:other-elements(..)}',   '/package') " name="remove_keyword={template:this-element()}"/></td>
      </tr>
  </axsl:template>
</axsl:stylesheet>
