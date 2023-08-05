import unittest
from xml.dom import Node
from amara import domtools

#Tests examples given in the manual
class TestMJ030815(unittest.TestCase):
    XML = """\
<?xml version="1.0" encoding="iso-8859-1"?>
<labels>
  <label id='ep' added="2003-06-10">
    <name>Ezra Pound</name>
    <address>
      <street>45 Usura Place</street>
      <city>Hailey</city>
      <province>ID</province>
    </address>
  </label>
  <label id='tse' added="2003-06-20">
    <name>Thomas Eliot</name>
    <address>
      <street>3 Prufrock Lane</street>
      <city>Stamford</city>
      <province>CT</province>
    </address>
  </label>
  <label id="lh" added="2004-11-01">
    <name>Langston Hughes</name>
    <address>
      <street>10 Bridge Tunnel</street>
      <city>Harlem</city>
      <province>NY</province>
    </address>
  </label>
  <label id="co" added="2004-11-15">
    <name>Christopher Okigbo</name>
    <address>
      <street>7 Heaven's Gate</street>
      <city>Idoto</city>
      <province>Anambra</province>
    </address>
  </label>
</labels>
"""
    
    def testPushFromString(self):
        results = []
        for docfrag in domtools.pushdom(self.XML, u'/labels/label'):
            label = docfrag.firstChild
            name = label.xpath('string(name)')
            city = label.xpath('string(address/city)')
            if name.lower().find('eliot') != -1:
                results.append(city)
        self.assertEqual(results, [u'Stamford'])
        return


#Tests interesting patterns of XML documents with pushbind

LABELS = """\
<?xml version="1.0" encoding="iso-8859-1"?>
<labels>
  <label id="tse" added="2003-06-20">
    <name>Thomas Eliot</name>
    <address>
      <street>3 Prufrock Lane</street>
      <city>Stamford</city>
      <state>CT</state>
    </address>
    <quote>
      <emph>Midwinter Spring</emph> is its own season&#8230;
    </quote>
  </label>
  <label id="ep" added="2003-06-10">
    <name>Ezra Pound</name>
    <address>
      <street>45 Usura Place</street>
      <city>Hailey</city>
      <state>ID</state>
    </address>
    <quote>
      What thou lovest well remains, the rest is dross&#8230;
    </quote>
  </label>
  <!-- Throw in 10,000 more records just like this -->
  <label id="lh" added="2004-11-01">
    <name>Langston Hughes</name>
    <address>
      <street>10 Bridge Tunnel</street>
      <city>Harlem</city>
      <state>NY</state>
    </address>
  </label>
</labels>
"""

ROOT_GI_IN_CHILD = """\
<A>
  <A>One</A>
  <B>Two</B>
</A>
"""

MIXED_TOPLEVEL_CHILDREN_1 = """\
<A>
  <B id="1">One</B>
  <C id="2">Two</C>
  <B id="3">Three</B>
  <C id="3">Four</C>
</A>
"""

MIXED_TOPLEVEL_CHILDREN_2 = """\
<A>
  <B id="1">One</B>
  <C id="2">Two</C>
  <D id="3">Three</D>
  <B id="4">Four</B>
  <C id="5">Five</C>
  <D id="6">Six</D>
</A>
"""

MIXED_TOPLEVEL_CHILDREN_AND_GRANDKIDS = """\
<A>
  <B id="1">One</B>
  <C id="2">
    <B id="2.1">Two</B>
  </C>
  <B id="3">
    <C id="3.1">Three</C>
  </B>
  <C id="4">Three</C>
</A>
"""

ROOT_GI_IN_CHILD_GRANDCHILD = """\
<A>
  <A>
    <A>A One</A>
    <B>A Two</B>
  </A>
  <B>
    <A>B One</A>
    <B>B Two</B>
  </B>
</A>
"""

QNAME_CLASH_1 = """\
<a xmlns='http://example.com/ns1'>
  <a>One</a>
  <a xmlns='http://example.com/ns2'>Two</a>
  <b>Three</b>
</a>
"""


class TestRealWorld(unittest.TestCase):
    def testXmlcomArticle(self):
        names = []
        cities = []
        for docfrag in domtools.pushdom(LABELS, u'labels/label'):
            label = docfrag.firstChild
            name = label.xpath('string(name)')
            names.append(name)
            city = label.xpath('string(address/city)')
            cities.append(city)
        self.assertEqual(names, [u"Thomas Eliot", u"Ezra Pound", u"Langston Hughes"])
        self.assertEqual(cities, [u"Stamford", u"Hailey", u"Harlem"])
        return

class XTestBasicPushdom(unittest.TestCase):
    #def setUp(self):
    #    return

    def testToplevelKidsAndGrandkids1(self):
        subtrees = domtools.pushdom(MIXED_TOPLEVEL_CHILDREN_AND_GRANDKIDS, u"/A/*")
        l1 = []
        l2 = []
        for st in subtrees:
            e = st.firstChild
            self.assertEqual(e.parentNode.nodeType, Node.DOCUMENT_FRAGMENT_NODE)
            l1.append(e.nodeName)
            l2.append(e.getAttributeNS(None, 'id'))
        self.assertEqual(l1, [u"B", u"C", u"B", u"C"])
        self.assertEqual(l2, [u"1", u"2", u"3", u"4"])
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testToplevelKidsAndGrandkids2(self):
        subtrees = domtools.pushdom(MIXED_TOPLEVEL_CHILDREN_AND_GRANDKIDS, u"B")
        l1 = []
        for st in subtrees:
            e = st.firstChild
            self.assertEqual(e.parentNode.nodeType, Node.DOCUMENT_FRAGMENT_NODE)
            self.assertEqual(e.nodeName, u"B")
            l1.append(e.getAttributeNS(None, 'id'))
        self.assertEqual(l1, [u"1", u"2.1", u"3"])
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testQnameClash(self):
        PREFIXES = {u'ns1': u'http://example.com/ns1',
                    u'ns2': u'http://example.com/ns2'}
        subtrees = domtools.pushdom(QNAME_CLASH_1, u"/*/*")
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns2')
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')

        subtrees = domtools.pushdom(QNAME_CLASH_1, u"/ns1:a/*",
                                      prefixes=PREFIXES)
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns2')
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')

        subtrees = domtools.pushdom(QNAME_CLASH_1, u"/ns1:a",
                                      prefixes=PREFIXES)
        elem = subtrees.next().firstChild
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        self.assertEqual(len(elem.firstChild.nextSibling.childNodes), 1)
        return


if __name__ == '__main__':
    unittest.main()
