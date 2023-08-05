<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <!-- Find out some additional information. -->

  <xsl:variable name="cpu-socket" select="configuration/details/base-system/base-system-enum[@value = ../@value]/@cpu-socket"/>
  <xsl:variable name="interface" select="configuration/details/base-system/base-system-enum[@value = ../@value]/@interface"/>
  <xsl:variable name="storage" select="configuration/storage/storage-unit/@value"/>



  <!-- Descend into the document, including only relevant elements. -->

  <xsl:template match="cpu-enum">
    <xsl:if test="@cpu-socket = $cpu-socket or not(@cpu-socket)">
      <cpu-enum>
        <xsl:apply-templates select="@*"/>
        <xsl:apply-templates select="*"/>
      </cpu-enum>
    </xsl:if>
  </xsl:template>

  <xsl:template match="hard-disk-enum">
    <xsl:if test="@interface = $interface or not(@interface)">
      <hard-disk-enum>
        <xsl:apply-templates select="@*"/>
        <xsl:apply-templates select="*"/>
      </hard-disk-enum>
    </xsl:if>
  </xsl:template>

  <xsl:template match="accessory-enum">
    <xsl:if test="$storage[string() = current()/@storage] or not(@storage)">
      <accessory-enum>
        <xsl:apply-templates select="@*"/>
        <xsl:apply-templates select="*"/>
      </accessory-enum>
    </xsl:if>
  </xsl:template>



  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
