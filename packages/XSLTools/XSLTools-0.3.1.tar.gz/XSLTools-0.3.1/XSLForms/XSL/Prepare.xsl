<?xml version="1.0"?>
<!--
A stylesheet which takes lower-level template annotations and produces an output
stylesheet - something which is capable of transforming XML documents into Web
pages or other kinds of XML documents.

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
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>
  <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>



  <!-- Match the document itself. -->

  <xsl:template match="/">
    <axsl:stylesheet version="1.0">

      <axsl:output indent="yes"/>
      <!-- NOTE: Hard-coded doctypes to hopefully satisfy JavaScript code. -->
      <!-- doctype-public="-//W3C//DTD XHTML 1.1//EN"
        doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd" -->

      <!-- Include internationalisation (i18n) support if appropriate. -->
      <axsl:param name="translations"/>
      <axsl:param name="locale"/>

      <axsl:template match="/">

        <!-- Include the remaining attributes. -->
        <xsl:apply-templates select="@*"/>

        <!-- Process the elements. -->
        <xsl:apply-templates select="*"/>

      </axsl:template>
    </axsl:stylesheet>
  </xsl:template>



  <!-- Match special conditional expression attributes. -->

  <xsl:template match="*[@template:if]">
    <axsl:if test="{@template:if}">
      <xsl:choose>
        <xsl:when test="@template:element">
          <xsl:call-template name="enter-element">
            <xsl:with-param name="other-elements" select="@template:element"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="enter-attribute"/>
        </xsl:otherwise>
      </xsl:choose>
    </axsl:if>
  </xsl:template>



  <!-- Match element references. -->

  <xsl:template match="*[not(@template:if) and @template:element]">
    <xsl:call-template name="enter-element">
      <xsl:with-param name="other-elements" select="@template:element"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="enter-element">
    <xsl:param name="other-elements"/>
    <xsl:variable name="first-element" select="substring-before($other-elements, ',')"/>
    <xsl:variable name="remaining-elements" select="substring-after($other-elements, ',')"/>
    <xsl:choose>
      <xsl:when test="$first-element = ''">
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$other-elements"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$first-element"/>
          <xsl:with-param name="remaining-elements" select="$remaining-elements"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="next-element">
    <xsl:param name="first-element"/>
    <xsl:param name="remaining-elements"/>
    <axsl:for-each select="{$first-element}">
      <xsl:choose>
        <xsl:when test="$remaining-elements = ''">
          <xsl:call-template name="enter-attribute"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="enter-element">
            <xsl:with-param name="other-elements" select="$remaining-elements"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </axsl:for-each>
  </xsl:template>



  <!-- Match special expression attributes. -->

  <xsl:template match="*[not(@template:if) and not(@template:element) and (@template:attribute or @template:value or @template:expr)]">
    <xsl:call-template name="enter-attribute"/>
  </xsl:template>

  <xsl:template name="enter-attribute">
    <xsl:choose>
      <xsl:when test="@template:attribute">
        <axsl:choose>
          <axsl:when test="@{@template:attribute}">
            <axsl:variable name="this-name"><xsl:value-of select="@template:attribute"/></axsl:variable>
            <axsl:variable name="this-value" select="@{@template:attribute}"/>
            <xsl:call-template name="special-attributes"/>
          </axsl:when>
          <axsl:otherwise>
            <axsl:variable name="this-name"><xsl:value-of select="@template:attribute"/></axsl:variable>
            <axsl:variable name="this-value"></axsl:variable>
            <xsl:call-template name="special-attributes"/>
          </axsl:otherwise>
        </axsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="special-attributes"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="special-attributes">
    <xsl:choose>
      <xsl:when test="@template:effect = 'replace'">
        <xsl:call-template name="special-value"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates select="@*"/>
          <xsl:call-template name="expression-attributes"/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="expression-attributes">
    <xsl:if test="@template:expr and @template:expr-attr">
      <axsl:if test="{@template:expr}">
        <axsl:attribute name="{@template:expr-attr}"><xsl:value-of select="@template:expr-attr"/></axsl:attribute>
      </axsl:if>
    </xsl:if>
    <xsl:call-template name="special-value"/>
  </xsl:template>

  <xsl:template name="special-value">
    <xsl:choose>
      <!-- Insert the stated value. -->
      <xsl:when test="@template:value">
        <axsl:value-of select="{@template:value}"/>
      </xsl:when>
      <!-- Insert the translated value. -->
      <xsl:when test="@template:i18n">
        <xsl:call-template name="translated-value"/>
      </xsl:when>
      <!-- Just process the descendants. -->
      <xsl:otherwise>
        <xsl:apply-templates select="node()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Match internationalisation attributes. -->

  <xsl:template match="*[not(@template:if) and not(@template:element) and not(@template:attribute) and not(@template:value) and not(@template:expr) and @template:i18n]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:call-template name="translated-value"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template name="translated-value">
    <xsl:choose>
      <!-- Look for a translation of the contents. -->
      <xsl:when test="@template:i18n = '-'">
        <!-- NOTE: Quoting not done completely. -->
        <axsl:variable name="translation"
          select="$translations/translations/locale[code/@value=$locale]/translation[@value='{text()}']/text()"/>
        <xsl:call-template name="insert-translated-value"/>
      </xsl:when>
      <!-- Look for a named translation. -->
      <xsl:otherwise>
        <!-- NOTE: Quoting not done completely. -->
        <axsl:variable name="translation"
          select="$translations/translations/locale[code/@value=$locale]/translation[@value='{@template:i18n}']/text()"/>
        <xsl:call-template name="insert-translated-value"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="insert-translated-value">
    <axsl:choose>
      <!-- Insert the translated value. -->
      <axsl:when test="$translation">
        <axsl:value-of select="$translation"/>
      </axsl:when>
      <!-- Otherwise, just process the descendants. -->
      <axsl:otherwise>
        <xsl:apply-templates select="node()"/>
      </axsl:otherwise>
    </axsl:choose>
  </xsl:template>



  <!-- Remove template attributes. -->

  <xsl:template match="@template:element|@template:init|@template:attribute|@template:value|@template:expr|@template:expr-attr|@template:effect|@template:if|@template:i18n">
  </xsl:template>



  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
