<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Questionnaire Editor</title>
  <meta name="generator" content="amaya 8.1a, see http://www.w3.org/Amaya/"/>
  <link xmlns:xlink="http://www.w3.org/1999/xlink" href="styles/styles.css" rel="stylesheet" type="text/css"/>
</head>

<axsl:apply-templates select="questionnaire" mode="id2308782"/>
</html>
  </axsl:template>
  <axsl:template match="questionnaire" mode="id2308782">
    <body xmlns="http://www.w3.org/1999/xhtml">
<h1>Questionnaire Editor</h1>

<p>Enter questions and possible responses below.</p>

<form method="POST" action="">

  <table class="questionnaire">
    <axsl:apply-templates select="question" mode="id2308808"/>
  </table>

  <p>
  <input type="submit" value="Add question" name="add-question"/> to make
  the questionnaire longer.</p>

  <p>
  <input type="submit" value="Finish" name="finish"/> when all the questions
  and responses are ready.</p>
</form>
</body>
  </axsl:template>
  <axsl:template match="question" mode="id2308808">
    <tbody xmlns="http://www.w3.org/1999/xhtml">
      <tr>
        <th class="question">Question</th>
        <td class="question"><axsl:choose><axsl:when test="@question-text"><axsl:variable name="this-name">question-text</axsl:variable><axsl:variable name="this-value" select="@question-text"/><textarea cols="40" rows="4" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:when><axsl:otherwise><axsl:variable name="this-name">question-text</axsl:variable><axsl:variable name="this-value"/><textarea cols="40" rows="4" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:otherwise></axsl:choose></td>
        <td class="question-options">
          <input type="submit" value="Remove question" name="remove-question={template:this-element()}"/></td>
      </tr>
      <tr>
        <th class="response">Response</th>
        <td class="response"><axsl:choose><axsl:when test="@question-type"><axsl:variable name="this-name">question-type</axsl:variable><axsl:variable name="this-value" select="@question-type"/><input type="radio" value="text" name="{template:this-attribute()}"><axsl:if test="$this-value = 'text'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">question-type</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="text" name="{template:this-attribute()}"><axsl:if test="$this-value = 'text'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose> Text</td>
        <td/>
      </tr>
      <tr>
        <td class="response"/>
        <td class="response"><axsl:choose><axsl:when test="@response-text"><axsl:variable name="this-name">response-text</axsl:variable><axsl:variable name="this-value" select="@response-text"/><input type="text" size="40" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">response-text</axsl:variable><axsl:variable name="this-value"/><input type="text" size="40" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        <td/>
      </tr>
      <tr>
        <td class="response"/>
        <td class="response"><axsl:choose><axsl:when test="@question-type"><axsl:variable name="this-name">question-type</axsl:variable><axsl:variable name="this-value" select="@question-type"/><input type="radio" value="choice" name="{template:this-attribute()}"><axsl:if test="$this-value = 'choice'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:when><axsl:otherwise><axsl:variable name="this-name">question-type</axsl:variable><axsl:variable name="this-value"/><input type="radio" value="choice" name="{template:this-attribute()}"><axsl:if test="$this-value = 'choice'"><axsl:attribute name="checked">checked</axsl:attribute></axsl:if></input></axsl:otherwise></axsl:choose> Multiple choice</td>
        <td/>
      </tr>
      <axsl:apply-templates select="choice" mode="id2308958"/>
      <tr>
        <td class="response"/>
        <td class="response"/>
        <td class="response">
          <input type="submit" value="Add choice" name="add-choice={template:this-element()}"/></td>
      </tr>
    </tbody>
  </axsl:template>
  <axsl:template match="choice" mode="id2308958">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <td class="response"/>
        <td class="choice"><axsl:choose><axsl:when test="@response-choice"><axsl:variable name="this-name">response-choice</axsl:variable><axsl:variable name="this-value" select="@response-choice"/><input type="text" size="40" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">response-choice</axsl:variable><axsl:variable name="this-value"/><input type="text" size="40" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        <td class="choice-options">
          <input type="submit" value="Remove choice" name="remove-choice={template:this-element()}"/></td>
      </tr>
  </axsl:template>
</axsl:stylesheet>
