<?xml version="1.0"?>
<!--
Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

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
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str">

  <!-- NOTE: Add various top-level definitions specific to XHTML. -->

  <xsl:output indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>



  <!-- Process the root element. -->

  <xsl:template match="/">
    <xsl:for-each select="*">
      <!-- NOTE: Not stating the namespace explicitly. -->
      <xsl:element name="{name()}">
        <xsl:for-each select="//@expr-prefix">
          <xsl:attribute namespace="{substring-after(string(), ' ')}" name="{substring-before(string(), ' ')}:{name()}"><xsl:value-of select="string()"/></xsl:attribute>
        </xsl:for-each>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:element>
    </xsl:for-each>
  </xsl:template>



  <!-- Remove the mangled template namespace declaration and other declarations. -->

  <xsl:template match="@template|@expr-prefix">
  </xsl:template>



  <!-- Match specific template attributes. -->

  <xsl:template match="@if|@element|@attribute|@attribute-field|@attribute-area|@attribute-button|@attribute-list-button|@selector-field|@multiple-choice-field|@multiple-choice-list-field|@multiple-choice-value|@multiple-choice-list-value|@multiple-choice-list-element|@effect|@value|@expr|@expr-attr|@i18n|@copy">
    <!-- Add the namespace. -->
    <xsl:attribute name="template:{local-name(.)}">
      <xsl:copy-of select="string(.)"/>
    </xsl:attribute>
  </xsl:template>



  <!-- Fix strings in attributes. -->

  <xsl:template name="fix-string">
    <xsl:copy-of select="str:decode-uri(string(.))"/>
  </xsl:template>



  <!-- Handle special attributes. -->

  <xsl:template match="@href|@src">
    <xsl:attribute name="{name(.)}">
      <xsl:call-template name="fix-string"/>
    </xsl:attribute>
  </xsl:template>



  <!-- Traverse unknown nodes. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
