<?xml version="1.0"?>
<axsl:stylesheet xmlns:dyn="http://exslt.org/dynamic" xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:template="http://www.boddie.org.uk/ns/xmltools/template" version="1.0" extension-element-prefixes="dyn">
  <axsl:output indent="yes"/>
  <axsl:param name="base-system"/>
  <axsl:param name="cpu"/>
  <axsl:param name="memory-unit"/>
  <axsl:param name="hard-disk"/>
  <axsl:param name="storage-unit"/>
  <axsl:param name="accessories"/>
  <axsl:param name="keyboard"/>
  <axsl:param name="mouse"/>
  <axsl:param name="screen"/>
  <axsl:template match="/">
    <axsl:apply-templates select="*" mode="id2300566"/>
  </axsl:template>
  <axsl:template match="configuration" mode="id2300566">
    <configuration>
      <axsl:apply-templates select="@*"/>
      <details>
        <axsl:apply-templates select="./details/@*"/>
        <base-system>
          <axsl:apply-templates select="./details/base-system/@*"/>
          <axsl:for-each select="$base-system/base-system/base-system-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </base-system>
        <cpu>
          <axsl:apply-templates select="./details/cpu/@*"/>
          <axsl:for-each select="$cpu/cpu/cpu-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </cpu>
      </details>
      <memory>
        <axsl:apply-templates select="./memory/@*"/>
        <axsl:apply-templates select="./memory/placeholder|./memory/memory-unit" mode="id2278388"/>
      </memory>
      <hard-disks>
        <axsl:apply-templates select="./hard-disks/@*"/>
        <axsl:apply-templates select="./hard-disks/placeholder|./hard-disks/hard-disk" mode="id2278356"/>
      </hard-disks>
      <storage>
        <axsl:apply-templates select="./storage/@*"/>
        <axsl:apply-templates select="./storage/placeholder|./storage/storage-unit" mode="id2300826"/>
      </storage>
      <accessories>
        <axsl:apply-templates select="./accessories/@*"/>
        <axsl:variable name="values-accessory-enum" select="./accessories/accessory-enum/@value"/>
        <axsl:for-each select="$accessories/accessories/accessory-enum">
          <axsl:copy>
            <axsl:apply-templates select="@*"/>
            <axsl:if test="$values-accessory-enum[string() = current()/@value]">
              <axsl:attribute name="value-is-set">true</axsl:attribute>
            </axsl:if>
            <axsl:copy-of select="node()"/>
          </axsl:copy>
        </axsl:for-each>
      </accessories>
      <peripherals>
        <axsl:apply-templates select="./peripherals/@*"/>
        <keyboard>
          <axsl:apply-templates select="./peripherals/keyboard/@*"/>
          <axsl:for-each select="$keyboard/keyboard/keyboard-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </keyboard>
        <mouse>
          <axsl:apply-templates select="./peripherals/mouse/@*"/>
          <axsl:for-each select="$mouse/mouse/mouse-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </mouse>
        <screen>
          <axsl:apply-templates select="./peripherals/screen/@*"/>
          <axsl:for-each select="$screen/screen/screen-enum">
            <axsl:copy>
              <axsl:apply-templates select="@*"/>
              <axsl:copy-of select="node()"/>
            </axsl:copy>
          </axsl:for-each>
        </screen>
      </peripherals>
    </configuration>
  </axsl:template>
  <axsl:template match="memory-unit" mode="id2278388">
    <memory-unit>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$memory-unit/memory-unit/memory-unit-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
    </memory-unit>
  </axsl:template>
  <axsl:template match="hard-disk" mode="id2278356">
    <hard-disk>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$hard-disk/hard-disk/hard-disk-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
    </hard-disk>
  </axsl:template>
  <axsl:template match="storage-unit" mode="id2300826">
    <storage-unit>
      <axsl:apply-templates select="@*"/>
      <axsl:for-each select="$storage-unit/storage-unit/storage-unit-enum">
        <axsl:copy>
          <axsl:apply-templates select="@*"/>
          <axsl:copy-of select="node()"/>
        </axsl:copy>
      </axsl:for-each>
    </storage-unit>
  </axsl:template>
  <axsl:template match="@*|placeholder|node()">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300566">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300846">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2283479">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2283499">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278344">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278367">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2283482">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278388">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300817">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300550">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278356">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282893">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2283495">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300826">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298943">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298931">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282910">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300829">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298981">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2295119">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298964">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2295141">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298977">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2295164">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
