<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Dictionary Lookup</title>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>
<axsl:apply-templates select="words" mode="id2299412"/>
</html>
  </axsl:template>
  <axsl:template match="words" mode="id2299412">
    <body xmlns="http://www.w3.org/1999/xhtml">
<form action="" method="POST">

<axsl:apply-templates select="entry" mode="id2278656"/>
<p>
  <input type="submit" value="Add item" name="add={template:this-element()}"/>
</p>

</form>
</body>
  </axsl:template>
  <axsl:template match="entry" mode="id2278656">
    <div xmlns="http://www.w3.org/1999/xhtml"> <!-- id="{template:this-element()}" template:id="word-node" -->
  <p>
    Word: <axsl:choose><axsl:when test="@word"><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value" select="@word"/><input type="text" onkeypress="requestUpdate(         'matches',         '{template:this-attribute()}',         '{template:other-elements(matches)}',         '{template:other-attributes('word', matches)}',         '{template:element-path(template:this-element())}')" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value"/><input type="text" onkeypress="requestUpdate(         'matches',         '{template:this-attribute()}',         '{template:other-elements(matches)}',         '{template:other-attributes('word', matches)}',         '{template:element-path(template:this-element())}')" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
    <input type="submit" value="Search" name="search={template:this-element()}"/>
    <input type="submit" value="Remove" name="remove={template:this-element()}"/>
  </p>
  <axsl:apply-templates select="matches" mode="id2297619"/>
</div>
  </axsl:template>
  <axsl:template match="matches" mode="id2297619">
    <p xmlns="http://www.w3.org/1999/xhtml" id="{template:this-element()}" template:id="matches-node">
    Matches:
    <axsl:choose><axsl:when test="@word"><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value" select="@word"/><select name="{template:this-attribute()}">
      <!-- onchange="requestUpdate(
        'word',
        '{template:new-attribute('word')}',
        '{template:other-elements(..)}',
        '{template:other-attributes('word', ..)}',
        '/words/entry')" -->
      <axsl:apply-templates select="match-enum" mode="id2289248"/>
    </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">word</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
      <!-- onchange="requestUpdate(
        'word',
        '{template:new-attribute('word')}',
        '{template:other-elements(..)}',
        '{template:other-attributes('word', ..)}',
        '/words/entry')" -->
      <axsl:apply-templates select="match-enum" mode="id2289248"/>
    </select></axsl:otherwise></axsl:choose>
  </p>
  </axsl:template>
  <axsl:template match="match-enum" mode="id2289248">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@word}">
      <axsl:if test="@word = ../@word">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@word"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
