<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>PEP 241 Package Registry</title>
  <meta name="generator" content="amaya 8.1a, see http://www.w3.org/Amaya/"/>
  <link xmlns:xlink="http://www.w3.org/1999/xlink" href="styles/styles.css" rel="stylesheet" type="text/css"/>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>

<axsl:apply-templates select="package" mode="id2311105"/>
</html>
  </axsl:template>
  <axsl:template match="package" mode="id2311105">
    <body xmlns="http://www.w3.org/1999/xhtml">
<h1>PEP 241 Package Registry</h1>

<form method="POST">

  <table cellspacing="0" cellpadding="5">
    <tbody>
      <tr>
        <th class="heading" colspan="2">Summary</th>
      </tr>
      <tr>
        <th>Package name</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th>Package version</th>
        <td><axsl:choose><axsl:when test="@version"><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value" select="@version"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th>Summary</th>
        <td><axsl:choose><axsl:when test="@summary"><axsl:variable name="this-name">summary</axsl:variable><axsl:variable name="this-value" select="@summary"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">summary</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th>Description</th>
        <td><axsl:choose><axsl:when test="@description"><axsl:variable name="this-name">description</axsl:variable><axsl:variable name="this-value" select="@description"/><textarea cols="80" rows="5" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:when><axsl:otherwise><axsl:variable name="this-name">description</axsl:variable><axsl:variable name="this-value"/><textarea cols="80" rows="5" name="{template:this-attribute()}"><axsl:value-of select="$this-value"/></textarea></axsl:otherwise></axsl:choose></td>
      </tr>
      <axsl:apply-templates select="error" mode="id2311251"/>
      <tr>
        <th>Home page</th>
        <td><axsl:choose><axsl:when test="@home-page"><axsl:variable name="this-name">home-page</axsl:variable><axsl:variable name="this-value" select="@home-page"/><input type="text" size="80" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">home-page</axsl:variable><axsl:variable name="this-value"/><input type="text" size="80" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th>Licence</th>
        <td><axsl:choose><axsl:when test="@licence"><axsl:variable name="this-name">licence</axsl:variable><axsl:variable name="this-value" select="@licence"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">licence</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
      </tr>
      <tr>
        <th colspan="2" class="heading">Categories</th>
      </tr>
      <axsl:apply-templates select="categories" mode="id2311325"/>
      <tr>
        <th colspan="2" class="heading">Platforms</th>
      </tr>
    </tbody>
    <tbody template:id="platforms" id="platforms">
      <axsl:apply-templates select="platforms" mode="id2311402"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add platform!" onclick=" return requestUpdateArea(   'platforms',   '{template:other-attributes('name', .)},{template:selector-name('add_platform', .)}',   'platforms',   '{template:other-elements(platforms)}',   '/package') " name="add_platform={template:this-element()}"/></td>
      </tr>
    </tbody>
    <tbody template:id="supported-platforms" id="supported-platforms">
      <tr>
        <th colspan="2" class="heading">Supported platforms</th>
      </tr>
      <axsl:apply-templates select="supported-platforms" mode="id2311470"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add platform!" onclick=" return requestUpdateArea(   'supported-platforms',   '{template:other-attributes('name', .)},{template:selector-name('add_supported_platform', .)}',   'supported-platforms',   '{template:other-elements(supported-platforms)}',   '/package') " name="add_supported_platform={template:this-element()}"/></td>
      </tr>
    </tbody>
    <tbody template:id="keywords" id="keywords">
      <tr>
        <th colspan="2" class="heading">Keywords</th>
      </tr>
      <axsl:apply-templates select="keywords" mode="id2311559"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add keyword!" onclick=" return requestUpdateArea(   'keywords',   '{template:other-attributes('name', .)},{template:selector-name('add_keyword', .)}',   'keywords',   '{template:other-elements(keywords)}',   '/package') " name="add_keyword={template:this-element()}"/></td>
      </tr>
    </tbody>
    <tbody cellspacing="0" cellpadding="5" template:id="authors" id="authors">
      <tr>
        <th colspan="2" class="heading">Authors</th>
      </tr>
      <axsl:apply-templates select="authors" mode="id2311647"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add author!" onclick=" return requestUpdateArea(   'authors',   '{template:other-attributes('name', .)},{template:selector-name('add_author', .)}',   'authors',   '{template:other-elements(authors)}',   '/package') " name="add_author={template:this-element()}"/></td>
      </tr>
    </tbody>
    <tbody cellspacing="0" cellpadding="5" template:id="dependencies" id="dependencies">
      <tr>
        <th colspan="2" class="heading">Dependencies</th>
      </tr>
      <axsl:apply-templates select="dependencies" mode="id2311787"/>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Add dependency!" onclick=" return requestUpdateArea(   'dependencies',   '{template:other-attributes('name', .)},{template:selector-name('add_dependency', .)}',   'dependencies',   '{template:other-elements(dependencies)}',   '/package') " name="add_dependency={template:this-element()}"/></td>
      </tr>
    </tbody>
    <tbody>
      <tr>
        <th colspan="2" class="heading">Actions</th>
      </tr>
      <tr>
        <th/>
        <td>
          <input type="submit" value="Update!" name="update"/> 
          <input type="submit" value="Export!" name="export"/> 
          <input type="submit" value="Finish!" name="finish"/></td>
      </tr>
    </tbody>
  </table>
</form>
</body>
  </axsl:template>
  <axsl:template match="error" mode="id2311251">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th/>
        <axsl:choose><axsl:when test="@description-size"><axsl:variable name="this-name">description-size</axsl:variable><axsl:variable name="this-value" select="@description-size"/><td class="error">Only 100 characters
          can be used in a description.</td></axsl:when><axsl:otherwise><axsl:variable name="this-name">description-size</axsl:variable><axsl:variable name="this-value"/><td class="error">Only 100 characters
          can be used in a description.</td></axsl:otherwise></axsl:choose>
      </tr>
  </axsl:template>
  <axsl:template match="categories" mode="id2311325">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Categories</th>
        <td>
          <axsl:apply-templates select="category" mode="id2311342"/>
        </td>
      </tr>
  </axsl:template>
  <axsl:template match="category" mode="id2311342">
    <select xmlns="http://www.w3.org/1999/xhtml" multiple="multiple" name="{template:list-attribute('category-enum',&#10;            'value')}">
            <axsl:apply-templates select="category-enum" mode="id2311365"/>
          </select>
  </axsl:template>
  <axsl:template match="category-enum" mode="id2311365">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value-is-set">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="platforms" mode="id2311402">
    <axsl:apply-templates select="platform" mode="id2311402"/>
  </axsl:template>
  <axsl:template match="platform" mode="id2311402">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Platform name</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          <input type="submit" value="Remove!" onclick=" return requestUpdateArea(   'platforms',   '{template:selector-name('remove_platform', .)}',   'platforms',   '{template:other-elements(..)}',   '/package') " name="remove_platform={template:this-element()}"/></td>
      </tr>
  </axsl:template>
  <axsl:template match="supported-platforms" mode="id2311470">
    <axsl:apply-templates select="supported-platform" mode="id2311470"/>
  </axsl:template>
  <axsl:template match="supported-platform" mode="id2311470">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Platform name</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          <input type="submit" value="Remove!" onclick=" return requestUpdateArea(   'supported-platforms',   '{template:selector-name('remove_supported_platform', .)}',   'supported-platforms',   '{template:other-elements(..)}',   '/package') " name="remove_supported_platform={template:this-element()}"/></td>
      </tr>
  </axsl:template>
  <axsl:template match="keywords" mode="id2311559">
    <axsl:apply-templates select="keyword" mode="id2311559"/>
  </axsl:template>
  <axsl:template match="keyword" mode="id2311559">
    <tr xmlns="http://www.w3.org/1999/xhtml">
        <th>Keyword</th>
        <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
          <input type="submit" value="Remove!" onclick=" return requestUpdateArea(   'keywords',   '{template:selector-name('remove_keyword', .)}',   'keywords',   '{template:other-elements(..)}',   '/package') " name="remove_keyword={template:this-element()}"/></td>
      </tr>
  </axsl:template>
  <axsl:template match="authors" mode="id2311647">
    <axsl:apply-templates select="author" mode="id2311647"/>
  </axsl:template>
  <axsl:template match="author" mode="id2311647">
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author name</th>
          <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input type="submit" value="Remove!" onclick="   return requestUpdateArea(     'authors',     '{template:selector-name('remove_author', .)}',     'authors',     '{template:other-elements(..)},',     '/package')   " name="remove_author={template:this-element()}"/></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author contact</th>
          <td><axsl:choose><axsl:when test="@contact"><axsl:variable name="this-name">contact</axsl:variable><axsl:variable name="this-value" select="@contact"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">contact</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Author e-mail</th>
          <td><axsl:choose><axsl:when test="@e-mail"><axsl:variable name="this-name">e-mail</axsl:variable><axsl:variable name="this-value" select="@e-mail"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">e-mail</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
      </axsl:template>
  <axsl:template match="dependencies" mode="id2311787">
    <axsl:apply-templates select="dependency" mode="id2311787"/>
  </axsl:template>
  <axsl:template match="dependency" mode="id2311787">
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Package name</th>
          <td><axsl:choose><axsl:when test="@name"><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value" select="@name"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">name</axsl:variable><axsl:variable name="this-value"/><input type="text" size="20" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose>
            <input type="submit" value="Remove!" onclick="   return requestUpdateArea(     'dependencies',     '{template:selector-name('remove_dependency', .)}',     'dependencies',     '{template:other-elements(..)}',     '/package') " name="remove_dependency={template:this-element()}"/></td>
        </tr>
        <tr xmlns="http://www.w3.org/1999/xhtml">
          <th>Package version</th>
          <td><axsl:choose><axsl:when test="@version"><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value" select="@version"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:when><axsl:otherwise><axsl:variable name="this-name">version</axsl:variable><axsl:variable name="this-value"/><input type="text" size="10" name="{template:this-attribute()}" value="{$this-value}"/></axsl:otherwise></axsl:choose></td>
        </tr>
      </axsl:template>
</axsl:stylesheet>
