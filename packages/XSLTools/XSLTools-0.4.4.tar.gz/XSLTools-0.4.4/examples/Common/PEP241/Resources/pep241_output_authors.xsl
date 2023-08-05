<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <tbody xmlns="http://www.w3.org/1999/xhtml" cellspacing="0" cellpadding="5" template:id="authors" id="authors">
      <tr>
        <th colspan="2" class="heading">Authors</th>
      </tr>
      <axsl:apply-templates select="authors" mode="id2324786"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add author!" onclick=" return requestUpdateArea(   'authors',   '{template:other-attributes('name', .)},{template:selector-name('add_author', .)}',   'authors',   '{template:other-elements(authors)}',   '/package') " name="add_author={template:this-element()}"/></td>
      </tr>
    </tbody>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="authors" mode="id2324786">
    <axsl:apply-templates select="author" mode="id2324786"/>
  </axsl:template>
  <axsl:template match="author" mode="id2324786">
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author name</th>
          <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input type="submit" value="Remove!" onclick="   return requestUpdateArea(     'authors',     '{template:selector-name('remove_author', .)}',     'authors',     '{template:other-elements(..)},',     '/package')   " name="remove_author={template:this-element()}"/></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author contact</th>
          <td><axsl:choose><axsl:when test="@contact"><axsl:variable name="this-name">contact</axsl:variable><axsl:variable name="this-value" select="@contact"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">contact</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author e-mail</th>
          <td><axsl:choose><axsl:when test="@e-mail"><axsl:variable name="this-name">e-mail</axsl:variable><axsl:variable name="this-value" select="@e-mail"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">e-mail</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
      </axsl:template>
</axsl:stylesheet>
