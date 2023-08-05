<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Example</title>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="structure" mode="id2328778"/>
</html>
  </axsl:template>
  <axsl:template match="structure" mode="id2328778">
    <body xmlns="http://www.w3.org/1999/xhtml">
<form action="" method="POST">

<!-- Template text between the start and the interesting part. -->

<axsl:apply-templates select="item" mode="id2328793"/>
<p>
  <input type="submit" value="Add item" name="add={template:this-element()}"/>
</p>
<p>
  <input name="update" type="submit" value="Update"/>
</p>

<!-- Template text between the interesting part and the end. -->

</form>
</body>
  </axsl:template>
  <axsl:template match="item" mode="id2328793">
    <div xmlns="http://www.w3.org/1999/xhtml">
  <p>
    Some item: <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
    <input type="submit" value="Remove" name="remove={template:this-element()}"/>
  </p>
  <p>
    Item type:
    <axsl:apply-templates select="type" mode="id2328836"/>
  </p>
  <axsl:apply-templates select="options" mode="id2328881"/>
  <p>
    Itself containing more items:
  </p>
  <axsl:apply-templates select="subitem" mode="id2328903"/>
  <p>
    <input type="submit" value="Add subitem" name="add2={template:this-element()}"/>
  </p>
</div>
  </axsl:template>
  <axsl:template match="type" mode="id2328836">
    <select xmlns="http://www.w3.org/1999/xhtml" multiple="multiple" onchange="requestUpdate(         'comments',         '{template:list-attribute('type-enum', 'value')}',         '{template:other-elements(../options)}',         '{template:child-attribute('value', template:child-element('comment', 1, template:other-elements(../options)))}',         '/structure/item')" name="{template:list-attribute('type-enum',&#10;            'value')}">
      <axsl:apply-templates select="type-enum" mode="id2328864"/>
    </select>
  </axsl:template>
  <axsl:template match="type-enum" mode="id2328864">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value-is-set">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="template:i18n(text())"/>
    </option>
  </axsl:template>
  <axsl:template match="options" mode="id2328881">
    <p xmlns="http://www.w3.org/1999/xhtml" template:id="comment-node" id="{template:this-element()}">
    <axsl:apply-templates select="comment" mode="id2328890"/>
  </p>
  </axsl:template>
  <axsl:template match="comment" mode="id2328890">
    <span xmlns="http://www.w3.org/1999/xhtml">Comment:
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><textarea cols="40" rows="3" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><textarea cols="40" rows="3" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:otherwise></axsl:choose>
    </span>
  </axsl:template>
  <axsl:template match="subitem" mode="id2328903">
    <p xmlns="http://www.w3.org/1999/xhtml">
    Sub-item: <axsl:choose><axsl:when test="@subvalue"><axsl:variable name="this-name">subvalue</axsl:variable><axsl:variable name="this-value" select="@subvalue"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">subvalue</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
    <input type="submit" value="Remove" name="remove2={template:this-element()}"/>
  </p>
  </axsl:template>
</axsl:stylesheet>
