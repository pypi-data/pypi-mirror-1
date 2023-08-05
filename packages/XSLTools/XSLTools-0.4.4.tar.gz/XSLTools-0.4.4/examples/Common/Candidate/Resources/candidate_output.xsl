<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Candidate</title>
</head>
<axsl:apply-templates select="candidate" mode="id2288270"/>
</html>
  </axsl:template>
  <axsl:template match="candidate" mode="id2288270">
    <body xmlns="http://www.w3.org/1999/xhtml">
<form action="" method="POST">

<h1>Candidate Details</h1>

<table border="0" cellspacing="0" cellpadding="5" width="80%" align="left">
  <tbody>
    <tr>
      <th colspan="2">General</th>
    </tr>
    <axsl:apply-templates select="identity" mode="id2288322"/>
    <tr>
      <th width="30%">Work status</th>
      <td width="70%">
        <axsl:apply-templates select="status" mode="id2288393"/>
      </td>
    </tr>
    <tr>
      <th colspan="2">Skills</th>
    </tr>
    <axsl:apply-templates select="skills" mode="id2288444"/>
    <tr>
      <th width="30%"/>
      <td width="70%">
        <input type="submit" value="Add" name="add-skill={template:this-element()}"/>
      </td>
    </tr>
    <tr>
      <th colspan="2">Qualifications</th>
    </tr>
  </tbody>
  <axsl:apply-templates select="qualifications" mode="id2288506"/>
  <tbody>
    <tr>
      <th width="30%"/>
      <td width="70%">
        <input type="submit" value="Add" name="add-qualification={template:this-element()}"/>
      </td>
    </tr>
  </tbody>
  <tbody>
    <tr>
      <th colspan="2">Experience</th>
    </tr>
  </tbody>
  <axsl:apply-templates select="experience" mode="id2288643"/>
  <tbody>
    <tr>
      <th width="30%"/>
      <td width="70%">
        <input type="submit" value="Add" name="add-employment={template:this-element()}"/>
      </td>
    </tr>
    <tr>
      <th width="30%"/>
      <td width="70%">
        <input type="submit" name="show" value="Show..."/>
        <input type="submit" name="admin" value="Admin..."/>
      </td>
    </tr>
  </tbody>
</table>

</form>
</body>
  </axsl:template>
  <axsl:template match="identity" mode="id2288322">
    <tr xmlns="http://www.w3.org/1999/xhtml">
      <th width="30%">Name</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose><br/>
        Anonymous
        <axsl:choose><axsl:when test="@anonymous"><axsl:variable name="this-name">anonymous</axsl:variable><axsl:variable name="this-value" select="@anonymous"/><input value="true" type="checkbox" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">anonymous</axsl:variable><axsl:variable name="this-value"/><input value="true" type="checkbox" name="{template:this-attribute()}"><axsl:if test="$this-value = 'true'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose>
      </td>
    </tr>
  </axsl:template>
  <axsl:template match="status" mode="id2288393">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="status-enum" mode="id2288414"/>
        </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" name="{template:this-attribute()}">
          <axsl:apply-templates select="status-enum" mode="id2288414"/>
        </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="status-enum" mode="id2288414">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="skills" mode="id2288444">
    <axsl:apply-templates select="skill" mode="id2288444"/>
  </axsl:template>
  <axsl:template match="skill" mode="id2288444">
    <tr xmlns="http://www.w3.org/1999/xhtml">
      <th width="30%">Skill</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
        <input type="submit" value="Remove" name="remove={template:this-element()}"/>
      </td>
    </tr>
  </axsl:template>
  <axsl:template match="qualifications" mode="id2288506">
    <axsl:apply-templates select="qualification" mode="id2288506"/>
  </axsl:template>
  <axsl:template match="qualification" mode="id2288506">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
    <tr>
      <th width="30%">Course/Diploma/Title</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@title"><axsl:variable name="this-name">title</axsl:variable><axsl:variable name="this-value" select="@title"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">title</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
        <input type="submit" value="Remove" name="remove={template:this-element()}"/>
      </td>
    </tr>
    <tr>
      <th width="30%">Grade/Level/Class</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@grade"><axsl:variable name="this-name">grade</axsl:variable><axsl:variable name="this-value" select="@grade"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">grade</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
      </td>
    </tr>
    <tr>
      <th width="30%">Institution</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@institution"><axsl:variable name="this-name">institution</axsl:variable><axsl:variable name="this-value" select="@institution"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">institution</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
      </td>
    </tr>
  </tbody>
  </axsl:template>
  <axsl:template match="experience" mode="id2288643">
    <axsl:apply-templates select="employment" mode="id2288643"/>
  </axsl:template>
  <axsl:template match="employment" mode="id2288643">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
    <tr>
      <th width="30%">Employment</th>
      <td width="70%">
        From <axsl:choose><axsl:when test="@from"><axsl:variable name="this-name">from</axsl:variable><axsl:variable name="this-value" select="@from"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">from</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
        to <axsl:choose><axsl:when test="@to"><axsl:variable name="this-name">to</axsl:variable><axsl:variable name="this-value" select="@to"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">to</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
        <input type="submit" value="Remove" name="remove={template:this-element()}"/>
      </td>
    </tr>
    <tr>
      <th width="30%">Employer</th>
      <td width="70%">
        <axsl:choose><axsl:when test="@employer"><axsl:variable name="this-name">employer</axsl:variable><axsl:variable name="this-value" select="@employer"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">employer</axsl:variable><axsl:variable name="this-value"/><input type="text" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
      </td>
    </tr>
  </tbody>
  </axsl:template>
</axsl:stylesheet>
