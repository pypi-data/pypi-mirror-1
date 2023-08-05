<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>
<xsl:param name="modname"/>
<xsl:template match="/">
    <html><head><title>Coverage Results for <xsl:value-of select="$modname"/></title>
    <link rel="stylesheet" type="text/css" href="coverage.css"/></head>
    <body>
    <h2>Coverage Results for <xsl:value-of select="$modname"/></h2>
    <div class="annotated-source-code">
    <table width="100%">
    <xsl:for-each select="/coverageAnnotation/line">
        <xsl:variable name="lineno" select="position()"/>
        <xsl:choose>
            <xsl:when test="@executable='false'">
                <!--<div class="annotation-line non-exec">-->
                <tr class="annotation-line non-exec">
                <td class="non-exec"><xsl:value-of select="$lineno"/></td>
                <td><pre><xsl:value-of select="."/></pre></td></tr>
            </xsl:when>
            <xsl:when test="@executable='true' and @covered='true'">
                <tr class="annotation-line executable covered">
                <td class="covered"><xsl:value-of select="$lineno"/></td>
                <td><pre><xsl:value-of select="."/></pre></td></tr>
            </xsl:when>
            <xsl:otherwise>
                <tr class="annotation-line executable uncovered">
                <td class="uncovered"><xsl:value-of select="$lineno"/></td>
                <td><pre><xsl:value-of select="."/></pre></td></tr>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:for-each>
    </table>
    </div></body></html>
</xsl:template>
</xsl:stylesheet>

