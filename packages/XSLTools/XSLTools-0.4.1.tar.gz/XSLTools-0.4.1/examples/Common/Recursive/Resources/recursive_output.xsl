<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Recursive Example</title>
</head>
<axsl:apply-templates select="recursive" mode="id2288166"/>
</html>
  </axsl:template>
  <axsl:template match="recursive" mode="id2288166">
    <body xmlns="http://www.w3.org/1999/xhtml">
<form action="" method="POST">

<!-- Template text between the start and the interesting part. -->

<axsl:apply-templates select="list" mode="id2273295"/>
<p>
  <input type="submit" value="Add list" name="add-list={template:this-element()}"/>
</p>

<!-- Template text between the interesting part and the end. -->

</form>
</body>
  </axsl:template>
  <axsl:template match="list" mode="id2273295">
    <div xmlns="http://www.w3.org/1999/xhtml">
  <p>This is a list called <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></p>
  <p>
    <input type="submit" value="Remove list" name="remove={template:this-element()}"/>
    <input type="submit" value="Add item to list" name="add-item={template:this-element()}"/>
  </p>
  <ul>
    <axsl:apply-templates select="item" mode="id2304573"/>
  </ul>
</div>
  </axsl:template>
  <axsl:template match="item" mode="id2304573">
    <li xmlns="http://www.w3.org/1999/xhtml">
      <p>This is an item called <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></p>
      <p>
        <input type="submit" value="Remove item" name="remove={template:this-element()}"/>
        <input type="submit" value="Add list here" name="add-list={template:this-element()}"/>
      </p>
      <axsl:apply-templates select="list" mode="id2273295"/>
    </li>
  </axsl:template>
  <axsl:template match="list" mode="id2323505">
    <p xmlns="http://www.w3.org/1999/xhtml">List goes here...</p>
  </axsl:template>
</axsl:stylesheet>
