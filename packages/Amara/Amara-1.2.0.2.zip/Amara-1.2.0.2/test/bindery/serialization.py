#Tests XSLT transforms on bindery nodes

import unittest
import amara

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

import sys

XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

class TestSerialization(unittest.TestCase):
    XML1 = '<doc><foo/></doc>'
    XML2 = '<doc xmlns:a="urn:bogus:a"><hidden attr="b:beta"/></doc>'
    XML3 = '<a:doc xmlns:a="urn:bogus:a"><a:foo/></a:doc>'
    def testAddNsDecl1(self):
        EXPECTED = XMLDECL + '<doc xmlns:a="urn:bogus:a"><foo/></doc>'
        doc = amara.parse(self.XML1)
        result = doc.xml(force_nsdecls={u'a': u'urn:bogus:a'})
        self.assertEqual(EXPECTED, result)
        return

    def testAddNsDecl2(self):
        #Remember that declarations in the doc always trump forced decls, including the
        #Implicit declaration of null default namespace
        EXPECTED = XMLDECL + '<doc><foo/></doc>'
        doc = amara.parse(self.XML1)
        result = doc.xml(force_nsdecls={None: u'urn:bogus:default'})
        self.assertEqual(EXPECTED, result)
        return

    def testAddNsDecl3(self):
        EXPECTED = XMLDECL + '<a:doc xmlns="urn:bogus:default" xmlns:a="urn:bogus:a"><a:foo/></a:doc>'
        doc = amara.parse(self.XML3)
        result = doc.xml(force_nsdecls={None: u'urn:bogus:default'})
        self.assertEqual(EXPECTED, result)
        return

    def testQnamesInContent1(self):
        EXPECTED = XMLDECL + '<doc xmlns:b="urn:bogus:b"><hidden attr="b:beta"/></doc>'
        doc = amara.parse(self.XML2)
        result = doc.xml(force_nsdecls={u'b': u'urn:bogus:b'})
        self.assertEqual(EXPECTED, result)
        return

    def testQnamesInContent2(self):
        EXPECTED = XMLDECL + '<doc xmlns:a="urn:bogus:a" xmlns:b="urn:bogus:b"><hidden attr="b:beta"/></doc>'
        doc = amara.parse(self.XML2)
        result = doc.xml(force_nsdecls={u'a': u'urn:bogus:a', u'b': u'urn:bogus:b'})
        self.assertEqual(EXPECTED, result)
        return


if __name__ == '__main__':
    unittest.main()

