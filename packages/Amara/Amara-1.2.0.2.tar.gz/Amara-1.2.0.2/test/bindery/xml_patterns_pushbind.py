#Tests interesting patterns of XML documents with pushbind

import unittest
import amara
from amara import binderytools

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

SPECIAL_GIS_1 = """<class class="1">
  <class class="a0"/>
  <class class="a1"/>
  <class class="a2"/>
</class>
"""

SPECIAL_GIS_2 = """<for for="1">
  <class class="a0"/>
  <class class="a1"/>
  <class class="a2"/>
</for>
"""

ATTRIBUTES_1 = """<r><x/><x a=\"1\"/><y/></r>"""


class TestInterestingXmlPatterns(unittest.TestCase):
    #def setUp(self):
    #    return

    def testToplevelKidsAndGrandkids1(self):
        elems = amara.pushbind(MIXED_TOPLEVEL_CHILDREN_AND_GRANDKIDS, u"/A/*")
        l1 = []
        l2 = []
        for e in elems:
            self.assertEqual(e.xml_parent, None)
            l1.append(e.nodeName)
            l2.append(e.id)
            self.assert_(isinstance(e.id, unicode))
            if e.id == u"2":
                self.assertEqual(len(list(e.B)), 1)
            if e.id == u"3":
                self.assertEqual(len(list(e.C)), 1)
        self.assertEqual(l1, [u"B", u"C", u"B", u"C"])
        self.assertEqual(l2, [u"1", u"2", u"3", u"4"])
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testToplevelKidsAndGrandkids2(self):
        elems = amara.pushbind(MIXED_TOPLEVEL_CHILDREN_AND_GRANDKIDS, u"B")
        l1 = []
        for e in elems:
            self.assertEqual(e.xml_parent, None)
            self.assertEqual(e.nodeName, u"B")
            l1.append(e.id)
            self.assert_(isinstance(e.id, unicode))
            if e.id == u"1":
                self.assertRaises(AttributeError, lambda x=None: e.C)
            if e.id == u"3":
                self.assertEqual(len(list(e.C)), 1)
                self.assertEqual(unicode(e.C), u"Three")
                self.assertEqual(e.C.id, u"3.1")
        self.assertEqual(l1, [u"1", u"2.1", u"3"])
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testQnameClash(self):
        PREFIXES = {u'ns1': u'http://example.com/ns1',
                    u'ns2': u'http://example.com/ns2'}
        elems = amara.pushbind(QNAME_CLASH_1, u"/*/*")
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns2')
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')

        elems = amara.pushbind(QNAME_CLASH_1, u"/ns1:a/*",
                               prefixes=PREFIXES)
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns2')
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')

        elems = amara.pushbind(QNAME_CLASH_1, u"/ns1:a",
                               prefixes=PREFIXES)
        elem = elems.next()
        self.assertEqual(elem.namespaceURI, u'http://example.com/ns1')
        self.assertEqual(len(list(elem.a)), 1)
        self.assertEqual(len(list(elem.a_)), 1)
        self.assertEqual(len(list(elem.b)), 1)
        return

    def testSpecialGis1(self):
        elems = amara.pushbind(SPECIAL_GIS_1, u"/class/*")
        l = []
        for e in elems:
            self.assertEqual(e.nodeName, u"class")
            l.append(e.class_)
            self.assert_(isinstance(e.class_, unicode))
        self.assertEqual(l, [u"a0", u"a1", u"a2"])
        return

    def testSpecialGis2(self):
        elems = amara.pushbind(SPECIAL_GIS_2, u"/for/*")
        l = []
        for e in elems:
            self.assertEqual(e.nodeName, u"class")
            l.append(e.class_)
            self.assert_(isinstance(e.class_, unicode))
        self.assertEqual(l, [u"a0", u"a1", u"a2"])
        return

    def testAttributePatterns(self):
        patterns = {
            u'@a': [(2, u'a')],
            u'*/@a': [(2, u'a')],
            u'@a|r': [(1, u'r')],
            u'r|@a': [(1, u'r')],
            u'@a|x': [(1, u'x'), (1, u'x')],
            u'x|@a': [(1, u'x'), (1, u'x')],
            u'@a|y': [(2, u'a'), (1, u'y')],
            u'y|@a': [(2, u'a'), (1, u'y')],
            u'@a|r/x': [(1, u'x'), (1, u'x')],
            u'r/x|@a': [(1, u'x'), (1, u'x')],
            u'@a|r/y': [(2, u'a'), (1, u'y')],
            u'r/y|@a': [(2, u'a'), (1, u'y')],
            }
        for pat in patterns:
            nodes = amara.pushbind(ATTRIBUTES_1, pat)
            self.assertEqual(patterns[pat], [(n.nodeType, n.nodeName) for n in nodes])
        return


if __name__ == '__main__':
    unittest.main()


