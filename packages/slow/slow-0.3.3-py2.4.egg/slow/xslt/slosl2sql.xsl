<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:slosl="http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/slosl"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    >

  <xsl:output method="text" encoding="utf-8"/>

  <xsl:template match="slosl:statement[boolean(@selected) and count(slosl:parent) = 1]">
    <xsl:apply-templates select="." mode="create_view" />
  </xsl:template>

  <xsl:template match="slosl:select" mode="create_view">
    <xsl:if test="not boolean($skip_create)">
      <xsl:text>CREATE VIEW </xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="slosl:where|slosl:having">
    <xsl:value-of select="local-name()" />
    <xsl:text> </xsl:text>
    <xsl:value-of select="math:serialize(./math:*, 'slosl-sql')"/>
  </xsl:template>

<!-- INCOMPLETE !! -->

</xsl:stylesheet>
