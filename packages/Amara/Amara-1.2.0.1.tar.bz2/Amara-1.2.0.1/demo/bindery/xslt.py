#The identity transform: duplicates the input to output
TRANSFORM = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""

SOURCE = """<spam id="eggs">I don't like spam</spam>"""

import amara
from Ft.Xml.Xslt import Processor
from Ft.Xml.InputSource import DefaultFactory
processor = Processor.Processor()
from Ft.Xml.Domlette import NonvalidatingReader
#Create a binding for the source document
doc = amara.parse(SOURCE)#, "http://spam.com/doc.xml")
src=DefaultFactory.fromString(TRANSFORM, "http://spam.com/identity.xslt")
processor.appendStylesheet(src)
result = processor.runNode(doc, "http://spam.com/doc.xml")
print result

