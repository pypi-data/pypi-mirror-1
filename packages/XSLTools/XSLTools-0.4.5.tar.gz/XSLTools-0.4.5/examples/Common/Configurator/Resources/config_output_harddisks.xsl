<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <axsl:for-each select="dyn:evaluate($element-path)">
      <div xmlns="http://www.w3.org/1999/xhtml" template:id="hard-disks-node" id="{template:this-element()}">
      <axsl:apply-templates select="hard-disk" mode="id2297367"/>

      <p>
        <input type="submit" value="{template:i18n('Add hard disk')}" name="add-hard-disk={template:this-element()}"/>
      </p>
    </div>
    </axsl:for-each>
  </axsl:template>
  <axsl:template match="hard-disk" mode="id2297367">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Hard disk drive']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Hard disk drive']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Hard disk drive</axsl:otherwise></axsl:choose></span>
        <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="hard-disk-enum" mode="id2297411"/>
        </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="hard-disk-enum" mode="id2297411"/>
        </select></axsl:otherwise></axsl:choose>
   
        <input type="submit" value="{template:i18n('Remove')}" name="remove-hard-disk={template:this-element()}"/>
      </p>
  </axsl:template>
  <axsl:template match="hard-disk-enum" mode="id2297411">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
