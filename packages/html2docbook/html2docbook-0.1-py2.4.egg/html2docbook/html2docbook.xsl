<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                exclude-result-prefixes="xsl fo html saxon">
<!--
http://wiki.docbook.org/topic/Html2DocBook
 -->

<xsl:output method="xml" indent="yes" omit-xml-declaration="yes" />

<!--
	Process only nodes within the body node.
 -->
<xsl:template match="html">
	<section>
		<xsl:apply-templates select="body" />
	</section>
</xsl:template>
<xsl:template match="body">
	<xsl:apply-templates />
</xsl:template>

<!--
	This template matches on all HTML header items and makes them into
    bridgeheads.
-->
<xsl:template match="h2">
	<bridgehead role="headline">
		<xsl:apply-templates/>
	</bridgehead>
</xsl:template>

<xsl:template match="h3">
	<bridgehead role="subheadline">
		<xsl:apply-templates/>
	</bridgehead>
</xsl:template>

<xsl:template match="h4">
	<bridgehead role="question">
		<xsl:apply-templates/>
	</bridgehead>
</xsl:template>

<xsl:template match=" h1 | h5 | h6 ">
	<bridgehead>
		<xsl:apply-templates/>
	</bridgehead>
</xsl:template>

<xsl:template match="blockquote">
	<blockquote>
		<xsl:apply-templates/>
	</blockquote>
</xsl:template>

<!--
	These templates perform one-to-one conversions of HTML elements into
    DocBook elements
-->

<!-- These templates perform one-to-one conversions of HTML elements into
     DocBook elements -->
<xsl:template match="p">
<!-- if the paragraph has no text (perhaps only a child <img>), don't
     make it a para -->
 <xsl:choose>
  <xsl:when test="normalize-space(.) = ''">
   <xsl:apply-templates/>
  </xsl:when>
  <xsl:otherwise>
 <para>
  <xsl:apply-templates/>
 </para>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>
<xsl:template match="pre">
 <programlisting>
  <xsl:apply-templates/>
 </programlisting>
</xsl:template>

<!-- Hyperlinks -->
<xsl:template match="a[contains(@href,'http://')]" priority="1.5">
 <ulink>
  <xsl:attribute name="url">
   <xsl:value-of select="normalize-space(@href)"/>
  </xsl:attribute>
  <xsl:apply-templates/>
 </ulink>
</xsl:template>

<xsl:template match="a[contains(@href,'#')]" priority="0.6">
 <xref>
  <xsl:attribute name="linkend">
   <xsl:call-template name="make_id">
    <xsl:with-param name="string" select="substring-after(@href,'#')"/>
   </xsl:call-template>
  </xsl:attribute>
 </xref>
</xsl:template>

<xsl:template match="a[@href != '']">
 <xref>
  <xsl:attribute name="linkend">
   <xsl:value-of select="$prefix"/>
   <xsl:text>_</xsl:text>
   <xsl:call-template name="make_id">
    <xsl:with-param name="string" select="@href"/>
   </xsl:call-template>
  </xsl:attribute>
 </xref>
</xsl:template>

<!-- Need to come up with good template for converting filenames into ID's -->
<xsl:template name="make_id">
 <xsl:param name="string" select="''"/>
 <xsl:variable name="fixedname">
  <xsl:call-template name="get_filename">
   <xsl:with-param name="path" select="translate($string,' \()','_/_')"/>
  </xsl:call-template>
 </xsl:variable>
 <xsl:choose>
  <xsl:when test="contains($fixedname,'.htm')">
   <xsl:value-of select="substring-before($fixedname,'.htm')"/>
  </xsl:when>
  <xsl:otherwise>
   <xsl:value-of select="$fixedname"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template name="string.subst">
 <xsl:param name="string" select="''"/>
 <xsl:param name="substitute" select="''"/>
 <xsl:param name="with" select="''"/>
 <xsl:choose>
  <xsl:when test="contains($string,$substitute)">
   <xsl:variable name="pre" select="substring-before($string,$substitute)"/>
   <xsl:variable name="post" select="substring-after($string,$substitute)"/>
   <xsl:call-template name="string.subst">
    <xsl:with-param name="string" select="concat($pre,$with,$post)"/>
    <xsl:with-param name="substitute" select="$substitute"/>
    <xsl:with-param name="with" select="$with"/>
   </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
   <xsl:value-of select="$string"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- Images -->
<!-- Images and image maps -->
<xsl:template match="img">
 <xsl:variable name="tag_name">
  <xsl:choose>
   <xsl:when test="boolean(parent::p) and
        boolean(normalize-space(parent::p/text()))">
    <xsl:text>inlinemediaobject</xsl:text>
   </xsl:when>
   <xsl:otherwise>mediaobject</xsl:otherwise>
  </xsl:choose>
 </xsl:variable>
 <xsl:element name="{$tag_name}">
  <imageobject>
   <xsl:call-template name="process.image"/>
  </imageobject>
 </xsl:element>
</xsl:template>

<xsl:template name="process.image">
 <imagedata>
<xsl:attribute name="fileref">
 <xsl:call-template name="make_absolute">
  <xsl:with-param name="filename" select="@src"/>
 </xsl:call-template>
</xsl:attribute>
<xsl:if test="@height != ''">
 <xsl:attribute name="depth">
  <xsl:value-of select="@height"/>
 </xsl:attribute>
</xsl:if>
<xsl:if test="@width != ''">
 <xsl:attribute name="width">
  <xsl:value-of select="@width"/>
 </xsl:attribute>
</xsl:if>
 </imagedata>
</xsl:template>

<xsl:template name="make_absolute">
 <xsl:param name="filename"/>
 <xsl:variable name="name_only">
  <xsl:call-template name="get_filename">
   <xsl:with-param name="path" select="$filename"/>
  </xsl:call-template>
 </xsl:variable>
 <xsl:value-of select="$graphics_location"/><xsl:value-of select="$name_only"/>
</xsl:template>

<xsl:template match="ul[count(*) = 0]">
 <xsl:message>Matched</xsl:message>
 <blockquote>
  <xsl:apply-templates/>
 </blockquote>
</xsl:template>

<xsl:template name="get_filename">
 <xsl:param name="path"/>
 <xsl:choose>
  <xsl:when test="contains($path,'/')">
   <xsl:call-template name="get_filename">
    <xsl:with-param name="path" select="substring-after($path,'/')"/>
   </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
   <xsl:value-of select="$path"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- LIST ELEMENTS -->
<xsl:template match="ul">
 <itemizedlist>
  <xsl:apply-templates/>
 </itemizedlist>
</xsl:template>

<xsl:template match="ol">
 <orderedlist>
  <xsl:apply-templates/>
 </orderedlist>
</xsl:template>

<!-- This template makes a DocBook variablelist out of an HTML definition list -->
<xsl:template match="dl">
 <variablelist>
  <xsl:for-each select="dt">
   <varlistentry>
    <term>
     <xsl:apply-templates/>
    </term>
    <listitem>
     <xsl:apply-templates select="following-sibling::dd[1]"/>
    </listitem>
   </varlistentry>
  </xsl:for-each>
 </variablelist>
</xsl:template>

<xsl:template match="dd">
 <xsl:choose>
  <xsl:when test="boolean(p)">
   <xsl:apply-templates/>
  </xsl:when>
  <xsl:otherwise>
   <para>
    <xsl:apply-templates/>
   </para>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template match="li">
 <listitem>
  <xsl:choose>
   <xsl:when test="count(p) = 0">
    <para>
     <xsl:apply-templates/>
    </para>
   </xsl:when>
   <xsl:otherwise>
    <xsl:apply-templates/>
   </xsl:otherwise>
  </xsl:choose>
 </listitem>
</xsl:template>

<xsl:template match="*">
 <xsl:message>No template for <xsl:value-of select="name()"/>
 </xsl:message>
 <xsl:apply-templates/>
</xsl:template>

<xsl:template match="@*">
 <xsl:message>No template for <xsl:value-of select="name()"/>
 </xsl:message>
 <xsl:apply-templates/>
</xsl:template>

<!-- inline formatting -->
<xsl:template match="b">
 <emphasis role="bold">
  <xsl:apply-templates/>
 </emphasis>
</xsl:template>
<xsl:template match=" i | em ">
 <emphasis>
  <xsl:apply-templates/>
 </emphasis>
</xsl:template>
<xsl:template match="u">
 <citetitle>
  <xsl:apply-templates/>
 </citetitle>
</xsl:template>

<!-- Ignored elements -->
<xsl:template match="hr"/>
<!--<xsl:template match="h1[1]|h2[1]|h3[1]" priority="1"/>-->
<xsl:template match="br"/>
<xsl:template match="p[normalize-space(.) = '' and count(*) = 0]"/>
<xsl:template match="text()">
 <xsl:choose>
  <xsl:when test="normalize-space(.) = ''"></xsl:when>
  <xsl:otherwise><xsl:copy/></xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- Workbench Hacks -->
<xsl:template match="div[contains(@style,'margin-left: 2em')]">
 <blockquote><para>
  <xsl:apply-templates/></para>
 </blockquote>
</xsl:template>

<xsl:template match="a[@href != ''
                      and not(boolean(ancestor::p|ancestor::li))]"
              priority="1">
 <para>
 <xref>
  <xsl:attribute name="linkend">
   <xsl:value-of select="$prefix"/>
   <xsl:text>_</xsl:text>
   <xsl:call-template name="make_id">
    <xsl:with-param name="string" select="@href"/>
   </xsl:call-template>
  </xsl:attribute>
 </xref>
 </para>
</xsl:template>

<xsl:template match="a[contains(@href,'#')
                    and not(boolean(ancestor::p|ancestor::li))]"
              priority="1.1">
 <para>
 <xref>
  <xsl:attribute name="linkend">
   <xsl:value-of select="$prefix"/>
   <xsl:text>_</xsl:text>
   <xsl:call-template name="make_id">
    <xsl:with-param name="string" select="substring-after(@href,'#')"/>
   </xsl:call-template>
  </xsl:attribute>
 </xref>
 </para>
</xsl:template>

<!-- Table conversion -->
<xsl:template match="table">
<!-- <xsl:variable name="column_count"
               select="saxon:max(.//tr,saxon:expression('count(td)'))"/> -->
 <xsl:variable name="column_count">
  <xsl:call-template name="count_columns">
   <xsl:with-param name="table" select="."/>
  </xsl:call-template>
 </xsl:variable>
 <informaltable>
  <tgroup>
   <xsl:attribute name="cols">
    <xsl:value-of select="$column_count"/>
   </xsl:attribute>
   <xsl:call-template name="generate-colspecs">
    <xsl:with-param name="count" select="$column_count"/>
   </xsl:call-template>
   <thead>
    <xsl:apply-templates select="tr[1]"/>
   </thead>
   <tbody>
    <xsl:apply-templates select="tr[position() != 1]"/>
   </tbody>
  </tgroup>
 </informaltable>
</xsl:template>

<xsl:template name="generate-colspecs">
 <xsl:param name="count" select="0"/>
 <xsl:param name="number" select="1"/>
 <xsl:choose>
  <xsl:when test="$count &lt; $number"/>
  <xsl:otherwise>
   <colspec>
    <xsl:attribute name="colnum">
     <xsl:value-of select="$number"/>
    </xsl:attribute>
    <xsl:attribute name="colname">
     <xsl:value-of select="concat('col',$number)"/>
    </xsl:attribute>
   </colspec>
   <xsl:call-template name="generate-colspecs">
    <xsl:with-param name="count" select="$count"/>
    <xsl:with-param name="number" select="$number + 1"/>
   </xsl:call-template>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template match="tr">
 <row>
  <xsl:apply-templates/>
 </row>
</xsl:template>

<xsl:template match="th|td">
 <xsl:variable name="position" select="count(preceding-sibling::*) + 1"/>
 <entry>
  <xsl:if test="@colspan &gt; 1">
   <xsl:attribute name="namest">
    <xsl:value-of select="concat('col',$position)"/>
   </xsl:attribute>
   <xsl:attribute name="nameend">
    <xsl:value-of select="concat('col',$position + number(@colspan) - 1)"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:if test="@rowspan &gt; 1">
   <xsl:attribute name="morerows">
    <xsl:value-of select="number(@rowspan) - 1"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:apply-templates/>
 </entry>
</xsl:template>

<xsl:template match="td_null">
 <xsl:apply-templates/>
</xsl:template>

<xsl:template name="count_columns">
 <xsl:param name="table" select="."/>
 <xsl:param name="row" select="$table/tr[1]"/>
 <xsl:param name="max" select="0"/>
 <xsl:choose>
  <xsl:when test="local-name($table) != 'table'">
   <xsl:message>Attempting to count columns on a non-table element</xsl:message>
  </xsl:when>
  <xsl:when test="local-name($row) != 'tr'">
   <xsl:message>Row parameter is not a valid row</xsl:message>
  </xsl:when>
  <xsl:otherwise>
   <!-- Count cells in the current row -->
   <xsl:variable name="current_count">
    <xsl:call-template name="count_cells">
     <xsl:with-param name="cell" select="$row/td[1]|$row/th[1]"/>
    </xsl:call-template>
   </xsl:variable>
   <!-- Check for the maximum value of $current_count and $max -->
   <xsl:variable name="new_max">
    <xsl:choose>
     <xsl:when test="$current_count &gt; $max">
      <xsl:value-of select="number($current_count)"/>
     </xsl:when>
     <xsl:otherwise>
      <xsl:value-of select="number($max)"/>
     </xsl:otherwise>
    </xsl:choose>
   </xsl:variable>
   <!-- If this is the last row, return $max, otherwise continue -->
   <xsl:choose>
    <xsl:when test="count($row/following-sibling::tr) = 0">
     <xsl:value-of select="$new_max"/>
    </xsl:when>
    <xsl:otherwise>
     <xsl:call-template name="count_columns">
      <xsl:with-param name="table" select="$table"/>
      <xsl:with-param name="row" select="$row/following-sibling::tr"/>
      <xsl:with-param name="max" select="$new_max"/>
     </xsl:call-template>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template name="count_cells">
 <xsl:param name="cell"/>
 <xsl:param name="count" select="0"/>
 <xsl:variable name="new_count">
  <xsl:choose>
   <xsl:when test="$cell/@colspan &gt; 1">
    <xsl:value-of select="number($cell/@colspan) + number($count)"/>
   </xsl:when>
   <xsl:otherwise>
    <xsl:value-of select="number('1') + number($count)"/>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:variable>
 <xsl:choose>
  <xsl:when test="count($cell/following-sibling::*) &gt; 0">
   <xsl:call-template name="count_cells">
    <xsl:with-param name="cell"
                    select="$cell/following-sibling::*[1]"/>
    <xsl:with-param name="count" select="$new_count"/>
   </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
   <xsl:value-of select="$new_count"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

</xsl:stylesheet>