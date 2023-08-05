<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" indent="yes" />

<xsl:param name="title" />
<xsl:param name="message" />

<xsl:template match="/">
  <html>
    <head>
        <title><xsl:value-of select="$title" /></title>
    </head>
    <body>
        <h1><xsl:value-of select="$message" /></h1>
    </body>
  </html>
</xsl:template>

</xsl:stylesheet>