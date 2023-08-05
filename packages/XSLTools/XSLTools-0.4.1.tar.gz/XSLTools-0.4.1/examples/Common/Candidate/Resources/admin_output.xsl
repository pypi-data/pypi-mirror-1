<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Administration</title>
</head>
<axsl:apply-templates select="admin" mode="id2281586"/>
</html>
  </axsl:template>
  <axsl:template match="admin" mode="id2281586">
    <body xmlns="http://www.w3.org/1999/xhtml">
<form action="" method="POST">

<h1>Candidate Profile</h1>

<table border="0" cellspacing="0" cellpadding="5" width="80%" align="left">
  <tbody>
    <tr>
      <th colspan="2">CVs</th>
    </tr>
    <axsl:apply-templates select="cvs" mode="id2281637"/>
    <tr>
      <th width="30%">
      </th>
      <td width="70%">
        <input value="New" type="submit" name="new={template:this-element()}"/>
      </td>
    </tr>
  </tbody>
</table>

</form>
</body>
  </axsl:template>
  <axsl:template match="cvs" mode="id2281637">
    <axsl:apply-templates select="cv" mode="id2281637"/>
  </axsl:template>
  <axsl:template match="cv" mode="id2281637">
    <tr xmlns="http://www.w3.org/1999/xhtml">
      <th width="30%">Name</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
        <input value="Show" type="submit" name="show={template:this-element()}"/>
        <input value="Edit" type="submit" name="edit={template:this-element()}"/>
        <input value="Remove" type="submit" name="remove={template:this-element()}"/>
      </td>
    </tr>
  </axsl:template>
</axsl:stylesheet>
