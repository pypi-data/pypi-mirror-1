<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:a="http://www.w3.org/2005/Atom"
                version="1.0">

  <xsl:strip-space elements="*" />
  <xsl:output method="html"/>
  
  <xsl:template match="/">
    <html>
      <body bgcolor="#FFFFFF">
       <h1><xsl:value-of select="/a:entry/a:title" /></h1>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
