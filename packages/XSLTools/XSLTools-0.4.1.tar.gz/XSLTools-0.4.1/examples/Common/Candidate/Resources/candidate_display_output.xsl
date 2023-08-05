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
<axsl:apply-templates select="candidate" mode="id2284560"/>
</html>
  </axsl:template>
  <axsl:template match="candidate" mode="id2284560">
    <body xmlns="http://www.w3.org/1999/xhtml">

<h1>Candidate Details</h1>

<table border="0" cellspacing="0" cellpadding="5" width="80%" align="left">
  <tbody>
    <axsl:apply-templates select="identity" mode="id2284589"/>
    <tr>
      <th width="30%">Work status</th>
      <td width="70%">
        <axsl:apply-templates select="status" mode="id2284653"/>
      </td>
    </tr>
    <tr>
      <th width="30%">Skills</th>
      <td width="70%">
        <axsl:apply-templates select="skills" mode="id2284677"/>
      </td>
    </tr>
    <tr>
      <th width="30%">Qualifications</th>
      <td width="70%" xml:space="preserve">
        <axsl:apply-templates select="qualifications" mode="id2284713"/>
      </td>
    </tr>
    <axsl:apply-templates select="experience" mode="id2284766"/>
  </tbody>
</table>

</body>
  </axsl:template>
  <axsl:template match="identity" mode="id2284589">
    <tr xmlns="http://www.w3.org/1999/xhtml">
      <th width="30%">Name</th>
      <td width="70%">
        <axsl:if test="not(@anonymous = 'true')"><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose></axsl:if>
        <axsl:if test="@anonymous = 'true'"><span><strong>Candidate name withheld</strong></span></axsl:if>
      </td>
    </tr>
  </axsl:template>
  <axsl:template match="status" mode="id2284653">
    <span xmlns="http://www.w3.org/1999/xhtml">
      <axsl:value-of select="@value"/>
    </span>
  </axsl:template>
  <axsl:template match="skills" mode="id2284677">
    <axsl:apply-templates select="skill" mode="id2284677"/>
  </axsl:template>
  <axsl:template match="skill" mode="id2284677">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/><br/>
        </span>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:value-of select="$this-value"/><br/>
        </span>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="qualifications" mode="id2284713">
    <axsl:apply-templates select="qualification" mode="id2284713"/>
  </axsl:template>
  <axsl:template match="qualification" mode="id2284713">
    <span xmlns="http://www.w3.org/1999/xhtml">
          <axsl:choose><axsl:when test="@title"><axsl:variable name="this-name">title</axsl:variable><axsl:variable name="this-value" select="@title"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">title</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
          <axsl:choose><axsl:when test="@grade"><axsl:variable name="this-name">grade</axsl:variable><axsl:variable name="this-value" select="@grade"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">grade</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
          <axsl:choose><axsl:when test="@institution"><axsl:variable name="this-name">institution</axsl:variable><axsl:variable name="this-value" select="@institution"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">institution</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
        </span>
  </axsl:template>
  <axsl:template match="experience" mode="id2284766">
    <axsl:apply-templates select="employment" mode="id2284766"/>
  </axsl:template>
  <axsl:template match="employment" mode="id2284766">
    <tr xmlns="http://www.w3.org/1999/xhtml">
      <th width="30%">
        From <axsl:choose><axsl:when test="@from"><axsl:variable name="this-name">from</axsl:variable><axsl:variable name="this-value" select="@from"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">from</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
        to <axsl:choose><axsl:when test="@to"><axsl:variable name="this-name">to</axsl:variable><axsl:variable name="this-value" select="@to"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">to</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
      </th>
      <td width="70%">
        <axsl:choose><axsl:when test="@employer"><axsl:variable name="this-name">employer</axsl:variable><axsl:variable name="this-value" select="@employer"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">employer</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose>
      </td>
    </tr>
  </axsl:template>
</axsl:stylesheet>
