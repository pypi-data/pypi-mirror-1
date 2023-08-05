<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <!-- Add or process comment elements inside item elements. -->
  <!-- This transformation must happen after type elements have been populated. -->

  <xsl:template match="item">
    <!-- Copy the element and its contents. -->
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- Ensure an options element. -->
      <xsl:call-template name="options"/>
      <xsl:apply-templates select="*[local-name() != 'options']"/>
    </xsl:copy>
  </xsl:template>

  <!-- Investigate options elements. -->

  <xsl:template name="options">
    <!-- Make the element. -->
    <options>
      <!-- Only for certain element types... -->
      <xsl:if test="type/type-enum[@value='P' and @value-is-set]">
        <!-- Add comments. -->
        <comment>
          <xsl:apply-templates select="options/comment/@value"/>
        </comment>
      </xsl:if>
    </options>
  </xsl:template>

  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
