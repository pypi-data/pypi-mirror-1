#Tests XSLT transforms on bindery nodes

import unittest
import amara
from amara import binderytools

from xpath import LABELS, XBEL, RSS

IDENTITY = """\
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
  <xsl:output method="xml" omit-xml-declaration="yes"/>
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>"""

USING_PARAMS = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='override' select='"abc"'/>
  <xsl:param name='list' select='foo'/>

  <xsl:template match="/">
    <doc>
      <overridden><xsl:value-of select='$override'/></overridden>
      <list><xsl:apply-templates select="$list"/></list>
    </doc>
  </xsl:template>

  <xsl:template match="text()">
    <item><xsl:value-of select="."/></item>
  </xsl:template>

</xsl:stylesheet>
"""


import sys

class TestXslt(unittest.TestCase):
    #def setUp(self):
    #    return

    def testIdentity(self):
        rules = [binderytools.ws_strip_element_rule(u'/*')]        if sys.hexversion < 0x2050000: return #FIXME Amara's doc order index impl is badly incomplete.  Just happens to manifest in Python 2.4
        for source in [LABELS, XBEL]:
            doc = amara.parse(source, rules=rules)
            firstpass = doc.xml_xslt(IDENTITY)
            doc = amara.parse(firstpass, rules=rules)
            self.assertEqual(doc.xml_xslt(IDENTITY), firstpass)
        return

    def testWithParams(self):
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<doc><overridden>xyz</overridden><list><item>a</item><item>b</item><item>c</item></list></doc>"""
        doc = amara.parse('<dummy/>')
        result = doc.xml_xslt(
            USING_PARAMS,
            params={'override' : 'xyz', 'list' : ['a', 'b', 'c']})
        self.assertEqual(expected, result)
        return


if __name__ == '__main__':
    unittest.main()

