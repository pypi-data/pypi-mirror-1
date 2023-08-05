<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Very Simple Login</title>
  <script type="text/javascript" src="{$root}scripts/sarissa.js"> </script>
  <script type="text/javascript" src="{$root}scripts/XSLForms.js"> </script>
</head>

<axsl:apply-templates select="login" mode="id2344460"/>
</html>
  </axsl:template>
  <axsl:template match="login" mode="id2344460">
    <body xmlns="http://www.w3.org/1999/xhtml">
<h1>Login</h1>

<form method="post">
  <table cellspacing="0" cellpadding="5" id="login-info">
    <thead>
      <tr>
        <th class="heading" colspan="2">Login</th>
      </tr>
    </thead>
    <tbody>
      <axsl:apply-templates select="error" mode="id2344504"/>
      <tr>
        <th>Username</th>
        <td><axsl:choose><axsl:when test="@username"><axsl:variable name="this-name">username</axsl:variable><axsl:variable name="this-value" select="@username"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">username</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th>Password</th>
        <td><axsl:choose><axsl:when test="@password"><axsl:variable name="this-name">password</axsl:variable><axsl:variable name="this-value" select="@password"/><input type="password" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">password</axsl:variable><axsl:variable name="this-value"/><input type="password" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <td colspan="2">
          <input type="submit" value="Log in!" name="login"/>
        </td>
      </tr>
    </tbody>
  </table>
</form>

</body>
  </axsl:template>
  <axsl:template match="error" mode="id2344504">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Error</th>
        <td><axsl:choose><axsl:when test="@message"><axsl:variable name="this-name">message</axsl:variable><axsl:variable name="this-value" select="@message"/><axsl:value-of select="$this-value"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">message</axsl:variable><axsl:variable name="this-value"/><axsl:value-of select="$this-value"/></axsl:otherwise></axsl:choose></td>
      </tr>
  </axsl:template>
</axsl:stylesheet>
