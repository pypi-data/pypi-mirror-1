<?xml version="1.0"?>
<!--
Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template"
  xmlns:dyn="http://exslt.org/dynamic"
  extension-element-prefixes="dyn">

  <xsl:output indent="yes"/>
  <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>

  <xsl:param name="element-id"/>



  <!-- Start at the top, finding only the specified element. -->

  <xsl:template match="/">
    <axsl:stylesheet version="1.0"
      xmlns:dyn="http://exslt.org/dynamic"
      extension-element-prefixes="dyn">

      <axsl:output indent="yes"/>
      <axsl:param name="element-path"/>

      <!-- NOTE: Hard-coded doctypes to hopefully satisfy JavaScript code. -->
      <!-- doctype-public="-//W3C//DTD XHTML 1.1//EN"
        doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd" -->

      <axsl:template match="/">

        <!-- Include the remaining attributes. -->
        <xsl:apply-templates select="@*"/>

        <!-- Process the elements. -->
        <xsl:for-each select="//*[@template:id=$element-id]">
          <axsl:for-each select="dyn:evaluate($element-path)">
            <xsl:copy>
              <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
          </axsl:for-each>
        </xsl:for-each>

      </axsl:template>
    </axsl:stylesheet>
  </xsl:template>



  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
