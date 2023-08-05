<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Very Simple Login Succeeded</title>
  <script type="text/javascript" src="{$root}scripts/sarissa.js"> </script>
  <script type="text/javascript" src="{$root}scripts/XSLForms.js"> </script>
</head>

<axsl:apply-templates select="success" mode="id2336248"/>
</html>
  </axsl:template>
  <axsl:template match="success" mode="id2336248">
    <body xmlns="http://www.w3.org/1999/xhtml">
<h1>Login Successful</h1>

  <p>Please proceed to the <a href="{@location}">application</a>.</p>

</body>
  </axsl:template>
</axsl:stylesheet>
