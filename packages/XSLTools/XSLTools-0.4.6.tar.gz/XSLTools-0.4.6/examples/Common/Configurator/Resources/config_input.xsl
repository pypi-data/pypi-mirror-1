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
    <axsl:apply-templates select="*" mode="id2275763"/>
  </axsl:template>
  <axsl:template match="configuration" mode="id2275763">
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
        <axsl:apply-templates select="./memory/placeholder|./memory/memory-unit" mode="id2289197"/>
      </memory>
      <hard-disks>
        <axsl:apply-templates select="./hard-disks/@*"/>
        <axsl:apply-templates select="./hard-disks/placeholder|./hard-disks/hard-disk" mode="id2275770"/>
      </hard-disks>
      <storage>
        <axsl:apply-templates select="./storage/@*"/>
        <axsl:apply-templates select="./storage/placeholder|./storage/storage-unit" mode="id2289368"/>
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
  <axsl:template match="memory-unit" mode="id2289197">
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
  <axsl:template match="hard-disk" mode="id2275770">
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
  <axsl:template match="storage-unit" mode="id2289368">
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
  <axsl:template match="placeholder" mode="id2275763">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2289370">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2273910">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2273925">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2289211">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2299341">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2289356">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2289197">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2275776">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2299352">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2275770">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2299253">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2286352">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2289368">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2299286">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2299346">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2295400">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2297390">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2273978">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2273997">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2274022">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2273973">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2274020">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
  <axsl:template match="placeholder" mode="id2298989">
    <axsl:copy>
      <axsl:apply-templates select="@*|node()"/>
    </axsl:copy>
  </axsl:template>
</axsl:stylesheet>
