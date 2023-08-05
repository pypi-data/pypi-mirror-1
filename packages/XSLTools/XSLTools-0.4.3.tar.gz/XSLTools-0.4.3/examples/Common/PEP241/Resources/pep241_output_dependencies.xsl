<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <tbody xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" template:id="dependencies" id="dependencies">
      <tr>
        <th colspan="2" class="heading">Dependencies</th>
      </tr>
      <axsl:apply-templates select="dependencies" mode="id2318423"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add dependency!" onclick=" return requestUpdateArea(   'dependencies',   '{template:other-attributes('name', .)},{template:selector-name('add_dependency', .)}',   'dependencies',   '{template:other-elements(dependencies)}',   '/package') " name="add_dependency={template:this-element()}"/></td>
      </tr>
    </tbody>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="dependencies" mode="id2318423">
    <axsl:apply-templates select="dependency" mode="id2318423"/>
  </axsl:template>
  <axsl:template match="dependency" mode="id2318423">
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Package name</th>
          <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input type="submit" value="Remove!" onclick="   return requestUpdateArea(     'dependencies',     '{template:selector-name('remove_dependency', .)}',     'dependencies',     '{template:other-elements(..)}',     '/package') " name="remove_dependency={template:this-element()}"/></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Package version</th>
          <td><axsl:choose><axsl:when test="@version"><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value" select="@version"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
      </axsl:template>
</axsl:stylesheet>
