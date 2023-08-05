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
    <axsl:apply-templates select="*" mode="id2278638"/>
  </axsl:template>
  <axsl:template match="configuration" mode="id2278638">
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
        <axsl:apply-templates select="./memory/placeholder|./memory/memory-unit" mode="id2298171"/>
      </memory>
      <hard-disks>
        <axsl:apply-templates select="./hard-disks/@*"/>
        <axsl:apply-templates select="./hard-disks/placeholder|./hard-disks/hard-disk" mode="id2300421"/>
      </hard-disks>
      <storage>
        <axsl:apply-templates select="./storage/@*"/>
        <axsl:apply-templates select="./storage/placeholder|./storage/storage-unit" mode="id2282410"/>
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
  <axsl:template match="memory-unit" mode="id2298171">
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
  <axsl:template match="hard-disk" mode="id2300421">
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
  <axsl:template match="storage-unit" mode="id2282410">
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
  <axsl:template match="placeholder" mode="id2278638">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282416">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282427">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298142">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298182">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290867">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290888">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298171">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300393">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2278645">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300421">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2300436">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2277991">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282410">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298256">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298255">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2282409">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298228">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290938">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290954">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290922">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2294921">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2290960">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2294946">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
