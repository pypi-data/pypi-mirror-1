<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>
<xsl:param name="packagename"/>
<xsl:template match="/">
    <html><head><title>Coverage Report for <xsl:value-of select="$packagename"/></title>
    <link rel="stylesheet" type="text/css" href="coverage.css"/></head>
    <body>
    <h2>Coverage Report for <xsl:value-of select="$packagename"/></h2>
    <table><tr><th>Module Name</th><th>Statements</th><th>Executed</th><th>Coverage</th></tr>
    <xsl:for-each select="//module">
        <tr>
            <td class="report-column">
                <a>
                <xsl:attribute name="href">
                   <xsl:text>coverage_</xsl:text><xsl:value-of select="translate(@name, '.', '-')"/><xsl:text>.html</xsl:text>
                </xsl:attribute>
                <xsl:value-of select="@name"/>
                </a>
            </td>
            <td class="report-column"><xsl:value-of select="@statements"/></td>
            <td class="report-column"><xsl:value-of select="@executed"/></td>
            <td class="report-column"><xsl:value-of select="@coverage"/></td>
        </tr>
    </xsl:for-each>
    </table>
    </body></html>
</xsl:template>
</xsl:stylesheet>

