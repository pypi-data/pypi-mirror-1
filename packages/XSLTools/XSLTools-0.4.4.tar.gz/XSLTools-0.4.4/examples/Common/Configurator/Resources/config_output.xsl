<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="translations"/>
  <axsl:param name="locale"/>
  <axsl:param name="element-path"/>
  <axsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='System Configurator']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='System Configurator']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>System Configurator</axsl:otherwise></axsl:choose></title>
  <meta name="generator" content="amaya 8.1a, see http://www.w3.org/Amaya/"/>
  <link xmlns:xlink="http://www.w3.org/1999/xlink" href="styles/styles.css" rel="stylesheet" type="text/css"/>
  <script type="text/javascript" src="scripts/sarissa.js"> </script>
  <script type="text/javascript" src="scripts/XSLForms.js"> </script>
</head>

<body>
<h1><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='System Configurator']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='System Configurator']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>System Configurator</axsl:otherwise></axsl:choose></h1>

<axsl:apply-templates select="configuration" mode="id2291244"/>
</body>
</html>
  </axsl:template>
  <axsl:template match="configuration" mode="id2291244">
    <form xmlns="http://www.w3.org/1999/xhtml" method="post" action="">
<div id="left">
  <axsl:apply-templates select="details" mode="id2291261"/>

  <axsl:apply-templates select="memory" mode="id2291384"/>
</div>
<div id="right">
  <axsl:apply-templates select="hard-disks" mode="id2291479"/>

  <axsl:apply-templates select="storage" mode="id2291560"/>

  <axsl:apply-templates select="accessories" mode="id2291638"/>
</div>
<div id="bottom">
  <axsl:apply-templates select="peripherals" mode="id2291699"/>

  <div class="price">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Price']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Price']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Price</axsl:otherwise></axsl:choose></h2>

    <p xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Total for this configuration:']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Total for this configuration:']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Total for this configuration:</axsl:otherwise></axsl:choose></span>
      <span><axsl:value-of select="sum(/configuration//*[@value-is-set]/@price) + sum(/configuration//*[@value = ../@value]/@price)"/></span></p>

    <p>
      <input type="submit" value="{template:i18n('Update!')}" name="update"/>
      <input type="submit" value="{template:i18n('Export!')}" name="export"/></p>
  </div>
</div>
</form>
  </axsl:template>
  <axsl:template match="details" mode="id2291261">
    <div xmlns="http://www.w3.org/1999/xhtml" class="details">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Base System']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Base System']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Base System</axsl:otherwise></axsl:choose></h2>

    <p xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Model']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Model']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Model</axsl:otherwise></axsl:choose></span>
      <axsl:apply-templates select="base-system" mode="id2291299"/>
    </p>

    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Processor']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Processor']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Processor</axsl:otherwise></axsl:choose></h2>

    <axsl:apply-templates select="cpu" mode="id2291359"/>
  </div>
  </axsl:template>
  <axsl:template match="base-system" mode="id2291299">
    <axsl:choose>
      <axsl:when test="@value">
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value" select="@value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" onchange="           requestUpdate('cpu', '{template:this-attribute()}',             '{template:other-elements(../cpu)}', '{template:other-attributes('value', ../cpu)}',             '/configuration/details');           requestUpdate('memory', '{template:this-attribute()}',             '{template:other-elements(../../memory)}', '{template:other-attributes('value', ../../memory/memory-unit)}',             '/configuration/memory');           requestUpdate('hard-disks', '{template:this-attribute()}',             '{template:other-elements(../../hard-disks)}',             '{template:other-attributes('value', ../../hard-disks/hard-disk)}', '/configuration/hard-disks')" name="{template:this-attribute()}">
        <axsl:apply-templates select="base-system-enum" mode="id2291335"/>
      </select>
      </axsl:when>
      <axsl:otherwise>
        <axsl:variable name="this-name">value</axsl:variable>
        <axsl:variable name="this-value"/>
        <select xmlns="http://www.w3.org/1999/xhtml" onchange="           requestUpdate('cpu', '{template:this-attribute()}',             '{template:other-elements(../cpu)}', '{template:other-attributes('value', ../cpu)}',             '/configuration/details');           requestUpdate('memory', '{template:this-attribute()}',             '{template:other-elements(../../memory)}', '{template:other-attributes('value', ../../memory/memory-unit)}',             '/configuration/memory');           requestUpdate('hard-disks', '{template:this-attribute()}',             '{template:other-elements(../../hard-disks)}',             '{template:other-attributes('value', ../../hard-disks/hard-disk)}', '/configuration/hard-disks')" name="{template:this-attribute()}">
        <axsl:apply-templates select="base-system-enum" mode="id2291335"/>
      </select>
      </axsl:otherwise>
    </axsl:choose>
  </axsl:template>
  <axsl:template match="base-system-enum" mode="id2291335">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="text()"/>
    </option>
  </axsl:template>
  <axsl:template match="cpu" mode="id2291359">
    <p xmlns="http://www.w3.org/1999/xhtml" template:id="cpu-node" id="{template:this-element()}" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='CPU']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='CPU']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>CPU</axsl:otherwise></axsl:choose></span>
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="cpu-enum" mode="id2291382"/>
      </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="cpu-enum" mode="id2291382"/>
      </select></axsl:otherwise></axsl:choose>
    </p>
  </axsl:template>
  <axsl:template match="cpu-enum" mode="id2291382">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="memory" mode="id2291384">
    <div xmlns="http://www.w3.org/1999/xhtml" class="memory">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Memory']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Memory']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Memory</axsl:otherwise></axsl:choose></h2>

    <div template:id="memory-node" id="{template:this-element()}">
      <axsl:apply-templates select="memory-unit" mode="id2291420"/>

      <p>
        <input type="submit" value="{template:i18n('Add memory')}" name="add-memory-unit={template:this-element()}"/>
      </p>
    </div>
  </div>
  </axsl:template>
  <axsl:template match="memory-unit" mode="id2291420">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Memory unit']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Memory unit']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Memory unit</axsl:otherwise></axsl:choose></span>
        <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="memory-unit-enum" mode="id2291440"/>
        </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="memory-unit-enum" mode="id2291440"/>
        </select></axsl:otherwise></axsl:choose>
   
        <input type="submit" value="{template:i18n('Remove')}" name="remove-memory-unit={template:this-element()}"/>
      </p>
  </axsl:template>
  <axsl:template match="memory-unit-enum" mode="id2291440">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="hard-disks" mode="id2291479">
    <div xmlns="http://www.w3.org/1999/xhtml" class="hard-disks">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Hard Disks']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Hard Disks']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Hard Disks</axsl:otherwise></axsl:choose></h2>

    <div template:id="hard-disks-node" id="{template:this-element()}">
      <axsl:apply-templates select="hard-disk" mode="id2291497"/>

      <p>
        <input type="submit" value="{template:i18n('Add hard disk')}" name="add-hard-disk={template:this-element()}"/>
      </p>
    </div>
  </div>
  </axsl:template>
  <axsl:template match="hard-disk" mode="id2291497">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Hard disk drive']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Hard disk drive']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Hard disk drive</axsl:otherwise></axsl:choose></span>
        <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="hard-disk-enum" mode="id2291530"/>
        </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
          <axsl:apply-templates select="hard-disk-enum" mode="id2291530"/>
        </select></axsl:otherwise></axsl:choose>
   
        <input type="submit" value="{template:i18n('Remove')}" name="remove-hard-disk={template:this-element()}"/>
      </p>
  </axsl:template>
  <axsl:template match="hard-disk-enum" mode="id2291530">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="storage" mode="id2291560">
    <div xmlns="http://www.w3.org/1999/xhtml" class="storage">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Additional Storage']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Additional Storage']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Additional Storage</axsl:otherwise></axsl:choose></h2>

    <axsl:apply-templates select="storage-unit" mode="id2291573"/>

    <p>
      <input type="submit" value="{template:i18n('Add storage')}" name="add-storage-unit={template:this-element()}"/></p>
  </div>
  </axsl:template>
  <axsl:template match="storage-unit" mode="id2291573">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Storage unit']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Storage unit']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Storage unit</axsl:otherwise></axsl:choose></span>
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select onchange="requestUpdate('accessories', '{template:other-attributes('value', ../storage-unit)}', '{template:other-elements(../../accessories)}', '{template:other-list-attributes('accessory-enum', 'value', ../../accessories)}', '/configuration')" name="{template:this-attribute()}">

        <axsl:apply-templates select="storage-unit-enum" mode="id2291609"/>
      </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select onchange="requestUpdate('accessories', '{template:other-attributes('value', ../storage-unit)}', '{template:other-elements(../../accessories)}', '{template:other-list-attributes('accessory-enum', 'value', ../../accessories)}', '/configuration')" name="{template:this-attribute()}">

        <axsl:apply-templates select="storage-unit-enum" mode="id2291609"/>
      </select></axsl:otherwise></axsl:choose>
   
      <input type="submit" value="{template:i18n('Remove')}" name="remove-storage-unit={template:this-element()}"/>
    </p>
  </axsl:template>
  <axsl:template match="storage-unit-enum" mode="id2291609">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="accessories" mode="id2291638">
    <div xmlns="http://www.w3.org/1999/xhtml" template:id="accessories-node" id="{template:this-element()}" class="accessories">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Accessories']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Accessories']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Accessories</axsl:otherwise></axsl:choose></h2>

    <select multiple="multiple" name="{template:list-attribute('accessory-enum',&#10;            'value')}">
      <axsl:apply-templates select="accessory-enum" mode="id2291675"/>
    </select>
  </div>
  </axsl:template>
  <axsl:template match="accessory-enum" mode="id2291675">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value-is-set">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="peripherals" mode="id2291699">
    <div xmlns="http://www.w3.org/1999/xhtml" class="peripherals">
    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Input Devices']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Input Devices']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Input Devices</axsl:otherwise></axsl:choose></h2>

    <axsl:apply-templates select="keyboard" mode="id2291714"/>

    <axsl:apply-templates select="mouse" mode="id2291752"/>

    <h2><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Display']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Display']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Display</axsl:otherwise></axsl:choose></h2>

    <axsl:apply-templates select="screen" mode="id2291792"/>
  </div>
  </axsl:template>
  <axsl:template match="keyboard" mode="id2291714">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Keyboard']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Keyboard']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Keyboard</axsl:otherwise></axsl:choose></span>
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="keyboard-enum" mode="id2291732"/>
      </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="keyboard-enum" mode="id2291732"/>
      </select></axsl:otherwise></axsl:choose>
    </p>
  </axsl:template>
  <axsl:template match="keyboard-enum" mode="id2291732">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="mouse" mode="id2291752">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Mouse']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Mouse']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Mouse</axsl:otherwise></axsl:choose></span>
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="mouse-enum" mode="id2291769"/>
      </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="mouse-enum" mode="id2291769"/>
      </select></axsl:otherwise></axsl:choose>
    </p>
  </axsl:template>
  <axsl:template match="mouse-enum" mode="id2291769">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
  <axsl:template match="screen" mode="id2291792">
    <p xmlns="http://www.w3.org/1999/xhtml" xml:space="preserve"><span><axsl:variable name="translation" select="$translations/translations/locale[code/@value=$locale]/translation[@value='Screen']/text()"/><axsl:variable name="translation-default" select="$translations/translations/locale[1]/translation[@value='Screen']/text()"/><axsl:choose><axsl:when test="$translation"><axsl:value-of select="$translation"/></axsl:when><axsl:when test="$translation-default"><axsl:value-of select="$translation-default"/></axsl:when><axsl:otherwise>Screen</axsl:otherwise></axsl:choose></span>
      <axsl:choose><axsl:when test="@value"><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value" select="@value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="screen-enum" mode="id2291810"/>
      </select></axsl:when><axsl:otherwise><axsl:variable name="this-name">value</axsl:variable><axsl:variable name="this-value"/><select name="{template:this-attribute()}">
        <axsl:apply-templates select="screen-enum" mode="id2291810"/>
      </select></axsl:otherwise></axsl:choose>
    </p>
  </axsl:template>
  <axsl:template match="screen-enum" mode="id2291810">
    <option xmlns="http://www.w3.org/1999/xhtml" value="{@value}">
      <axsl:if test="@value = ../@value">
        <axsl:attribute name="selected">selected</axsl:attribute>
      </axsl:if>
      <axsl:value-of select="@value"/>
    </option>
  </axsl:template>
</axsl:stylesheet>
