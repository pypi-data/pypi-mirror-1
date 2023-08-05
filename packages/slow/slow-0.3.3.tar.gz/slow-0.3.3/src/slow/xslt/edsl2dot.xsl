<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:edsl="http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/edsl"
    xmlns:l="local"
    >
  <xsl:output method="text" encoding="UTF-8" />

  <xsl:param name="graph_name">edsm_graph</xsl:param>

  <l:colours>
    <l:colour type="transition" >#000000</l:colour><!-- black   -->
    <l:colour type="message"    >#0000ff</l:colour><!-- blue    -->
    <l:colour type="event"      >#ff0000</l:colour><!-- red     -->
    <l:colour type="outputchain">#00ff00</l:colour><!-- green   -->
    <l:colour type="timer"      >#ff00ff</l:colour><!-- magenta -->
  </l:colours>

  <xsl:variable name="colours" select="document('')/*/l:colours">

  <xsl:template match="edsl:edsm">
    <xsl:text>digraph </xsl:text>
    <xsl:value-of select="$graph_name"/>
    <xsl:text> {</xsl:text>
    <xsl:call-template name="cr"/>

    <xsl:apply-templates
	select="./edsl:states/edsl:state[@name  = 'start']"
	mode="start-end-state"/>
    <xsl:apply-templates
	select="./edsl:states/edsl:state[@name != 'start']"/>
    <xsl:apply-templates
	select="./edsl:states/edsl:subgraph"/>
    <xsl:apply-templates
	select="./edsl:transitions/edsl:transition"/>

    <xsl:call-template name="cr"/>
    <xsl:text>}</xsl:text>
    <xsl:call-template name="cr"/>
  </xsl:template>

  <xsl:template match="edsl:subgraph">
    <xsl:variable name="entry" select="string(@entry_state)"/>
    <xsl:variable name="exit"  select="string(@exit_state)"/>

    <xsl:text>subgraph cluster_</xsl:text>
    <xsl:value-of select="@id"/>
    <xsl:text> {</xsl:text>
    <xsl:call-template name="cr"/>
    <xsl:apply-templates select="." mode="label"/>
    <xsl:call-template name="cr"/>

    <xsl:apply-templates
	select="./edsl:states/edsl:state[@id  = $entry or  @id  = $exit]"
	mode="start-end-state"/>
    <xsl:apply-templates
	select="./edsl:states/edsl:state[@id != $entry and @id != $exit]"/>
    <xsl:apply-templates
	select="./edsl:transitions/edsl:transition"/>

    <xsl:call-template name="cr"/>
    <xsl:text>}</xsl:text>
    <xsl:call-template name="cr"/>
  </xsl:template>

  <xsl:template match="edsl:state" mode="start-end-state">
    <xsl:text>"</xsl:text><xsl:value-of select="@id"/><xsl:text>"</xsl:text>
    <xsl:text> [ shape="box"</xsl:text>
    <xsl:apply-templates select="." mode="state-attributes"/>
    <xsl:text>]</xsl:text>
    <xsl:call-template name="cr"/>
  </xsl:template>

  <xsl:template match="edsl:state">
    <xsl:text>"</xsl:text><xsl:value-of select="@id"/><xsl:text>"</xsl:text>
    <xsl:text> [ shape="circle"</xsl:text>
    <xsl:apply-templates select="." mode="state-attributes"/>
    <xsl:text> ]</xsl:text>
    <xsl:call-template name="cr"/>
  </xsl:template>

  <xsl:template match="edsl:state" mode="state-attributes">
    <xsl:text>, </xsl:text>
    <xsl:apply-templates select="." mode="label"/>
  </xsl:template>

  <xsl:template match="edsl:transition">
    <xsl:variable name="type" select="@type"/>

    <xsl:text>"</xsl:text>
    <xsl:value-of select="string(./from_state/@ref)"/>
    <xsl:text>" -> "</xsl:text>
    <xsl:value-of select="string(./to_state/@ref)"/>
    <xsl:text>" [ color="</xsl:text>
    <xsl:value-of select="string($colours/l:colour[@type = $type])"/>
    <xsl:text>"</xsl:text>

    <xsl:if test="normalize-space(./readablename)">
      <xsl:text>, label="</xsl:text>
      <xsl:value-of select="normalize-space(./readablename)"/>
      <xsl:text>"</xsl:text>
    </xsl:if>

    <xsl:text> ]</xsl:text>
    <xsl:call-template name="cr"/>
  </xsl:template>

  <xsl:template match="edsl:*" mode="label">
    <xsl:text>label="</xsl:text>
    <xsl:choose>
      <xsl:when test="normalize-space(./readablename)">
	<xsl:value-of select="normalize-space(./readablename)"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="normalize-space(@name)"/></xsl:otherwise>
    </xsl:choose>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template name="cr">
    <xsl:text>&#10;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
