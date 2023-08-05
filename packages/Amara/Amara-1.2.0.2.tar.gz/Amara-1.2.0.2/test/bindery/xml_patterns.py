#Tests interesting patterns of XML documents

import unittest
import amara
import keyword


ROOT_MIXED_1 = "<A>x<B/>y</A>"

ROOT_MIXED_2 = """\
<A>x
  <B>Two</B>
y</A>
"""

ROOT_GI_IN_CHILD = """\
<A>
  <A>One</A>
  <B>Two</B>
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

#Jordan Gottlieb test case
JORDAN_GOTTLIEB_050120 = """\
<?xml version="1.0" encoding="UTF-8"?>
<box>this box has bubblewrap, in which is a bag and another box
  <bubblewrap>
    <box>stuff</box>
    <bag>bag inside the bubblewrap?</bag>
  </bubblewrap>
</box>"""

QNAME_CLASH_1 = """\
<a xmlns="http://example.com/ns1">
  <a>One</a>
  <a xmlns="http://example.com/ns2">Two</a>
  <b>Three</b>
</a>"""

FDRAKE_NS_EG = """\
<doc xmlns:a="http://xml.python.org/a"
     xmlns:A="http://xml.python.org/a"
     xmlns:b="http://xml.python.org/b"
     a:a="a" b:b="b"
     />
"""

RSALZ_NS_EG = """\
    <S:foo xmlns:S="http://example.com/1">
        <bar>test</bar>
        <bar xmlns='http://example.com/2'>test2</bar>
        <S:bar xmlns:S='http://example.com/2'>test2</S:bar>
    </S:foo>
"""

XSA = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xsa PUBLIC "-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML"
                     "http://www.garshol.priv.no/download/xsa/xsa.dtd">
<xsa>
  <vendor>
    <name>Fourthought, Inc.</name>
    <email>info@fourthought.com</email>
    <url>http://fourthought.com</url>
  </vendor>
  <product id="FourSuite">
    <name>4Suite</name>
    <version>1.0a1</version>
    <last-release>20030327</last-release>
    <info-url>http://4suite.org</info-url>
    <changes>
 - Begin the 1.0 release cycle
    </changes>
  </product>
</xsa>
"""

XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

#See http://www-128.ibm.com/developerworks/xml/library/x-namcar.html
BORDERLINE = """<org>
  <a:employee xmlns:a='urn:bogus:ns'>EP</a:employee>
  <b:employee xmlns:b='urn:bogus:ns'>TSE</b:employee>
</org>"""

BORDERLINE_DEFAULT = """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml">
    <p>boo</p>
</html>
"""

NEUROTIC = """
<h:memo xmlns:a='urn:bogus:ns'>
  <h:body xmlns:a='http://www.w3.org/1999/xhtml'>
    Now hear <h:i>this</h:i>
  </h:body>
</h:memo>"""

PSYCHOTIC = """<org xmlns:a='urn:bogus:ns' xmlns:b='urn:bogus:ns'>
  <a:employee>EP</a:employee>
  <b:employee>TSE</b:employee>
</org>
"""

SPECIAL_GIS_1 = """<class class="1">
  <ns/>
  <prefix/>
  <qname/>
  <ename/>
  <namer/>
  <naming_rule/>
</class>
"""

SPECIAL_GIS_2 = """<for for="1">
  <class/>
  <class/>
</for>
"""

from amara.bindery import RESERVED_NAMES
#Names that could potentially cause problems, usually because they could
#interfere with the trickery in bindery.create_element
TRICKY_NAMES = ['instance', 'local', 'qname', 'ns', 'globals', 'ename']


class TestInterestingXmlPatterns(unittest.TestCase):
    #def setUp(self):
    #    return

    def testMixed(self):
        doc = amara.parse(ROOT_MIXED_1)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(list(doc.A.B)), 1)
        self.assertEqual(len(list(doc.A.xml_child_elements)), 1)
        self.assertEqual(list(doc.A.xml_properties.keys()), [u'B'])
        self.assertEqual(len(doc.A.xml_children), 3)
        self.assertEqual(unicode(doc.A), u'xy')
        doc = amara.parse(ROOT_MIXED_2)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(list(doc.A.B)), 1)
        self.assertEqual(len(list(doc.A.xml_child_elements)), 1)
        self.assertEqual(list(doc.A.xml_properties.keys()), [u'B'])
        self.assertEqual(len(doc.A.xml_children), 3)
        self.assertEqual(unicode(doc.A), u'x\n  Two\ny')
        self.assertEqual(doc.A.xml_child_text, u'x\n  \ny')
        return

    def testRootGiInChild(self):
        doc = amara.parse(ROOT_GI_IN_CHILD)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(list(doc.A.A)), 1)
        self.assertEqual(len(list(doc.A.B)), 1)
        self.assertEqual(unicode(doc.A.A), u'One')
        self.assertEqual(unicode(doc[u'A'].A), u'One')
        self.assertEqual(unicode(doc.A[u'A']), u'One')
        self.assertEqual(unicode(doc[u'A'][u'A']), u'One')
        self.assertEqual(unicode(doc.A.B), u'Two')
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testRootGiInChildGrandchild(self):
        doc = amara.parse(ROOT_GI_IN_CHILD_GRANDCHILD)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(list(doc.A.A)), 1)
        self.assertEqual(len(list(doc.A.B)), 1)
        self.assertEqual(len(list(doc.A.A.A)), 1)
        self.assertEqual(len(list(doc.A.A.B)), 1)
        self.assertEqual(len(list(doc.A.B.A)), 1)
        self.assertEqual(len(list(doc.A.B.B)), 1)
        self.assertEqual(unicode(doc.A.A.A), u'A One')
        self.assertEqual(unicode(doc.A.A.B), u'A Two')
        self.assertEqual(unicode(doc.A.B.A), u'B One')
        self.assertEqual(unicode(doc.A.B.B), u'B Two')
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testJordanGottlieb050120(self):
        doc = amara.parse(JORDAN_GOTTLIEB_050120)
        self.assertEqual(len(list(doc.box)), 1)
        self.assertEqual(len(list(doc.box.bubblewrap)), 1)
        self.assertEqual(len(list(doc.box.bubblewrap.box)), 1)
        self.assertEqual(len(list(doc.box.bubblewrap.bag)), 1)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testQnameClash(self):
        doc = amara.parse(QNAME_CLASH_1)
        NS1 = u'http://example.com/ns1'
        NS2 = u'http://example.com/ns2'
        self.assertEqual(len(list(doc.a)), 1)
        self.assertEqual(len(list(doc.a.a)), 1)
        self.assertEqual(len(list(doc.a.a_)), 1)
        self.assertEqual(len(list(doc.a.b)), 1)
        self.assertEqual(unicode(doc.a.a), u'One')
        self.assertEqual(unicode(doc.a.a_), u'Two')
        self.assertEqual(unicode(doc.a.b), u'Three')
        self.assertEqual(unicode(doc[NS1, u'a'].a), u'One')
        self.assertEqual(unicode(doc[NS1, u'a'][NS1, u'a']), u'One')
        self.assertEqual(unicode(doc.a[NS1, u'a']), u'One')
        self.assertEqual(doc.xml(), XMLDECL+QNAME_CLASH_1)
        return

    def testQueryDefaultNs(self):
        doc = amara.parse(BORDERLINE_DEFAULT)
        #print doc.xmlns_prefixes
        self.assertEqual(len(doc.xml_xpath(u"//html:html")), 1)
        return

    def testSpecialGis1(self):
        doc = amara.parse(SPECIAL_GIS_1)
        self.assertEqual(len(list(doc.class_)), 1)
        self.assertEqual(doc.class_.class_, u"1")
        self.assertEqual(len(doc.xml_xpath(u"/class")), 1)
        return

    def testSpecialGis2(self):
        doc = amara.parse(SPECIAL_GIS_2)
        self.assertEqual(len(list(doc.for_)), 1)
        self.assertEqual(len(list(doc.for_.class_)), 2)
        self.assertEqual(len(doc.xml_xpath(u"/for")), 1)
        self.assertEqual(len(doc.xml_xpath(u"/for/class")), 2)
        return

    def testReservedNames(self):
        for name in RESERVED_NAMES:
            doc = amara.parse('<%s/>'%(name))
            self.assertEqual(len(list(getattr(doc, name+'_'))), 1)
            doc = amara.parse('<%(name)s><%(name)s/></%(name)s>'%{'name': name})
            self.assertEqual(len(list(getattr(doc, name+'_'))), 1)
            self.assertEqual(len(list(getattr(getattr(doc, name+'_'), name+'_'))), 1)
        return

    def testTrickyNames(self):
        for name in TRICKY_NAMES:
            doc = amara.parse('<%s/>'%(name))
            self.assertEqual(len(list(getattr(doc, name))), 1)
            doc = amara.parse('<%(name)s><%(name)s/></%(name)s>'%{'name': name})
            self.assertEqual(len(list(getattr(doc, name))), 1)
            self.assertEqual(len(list(getattr(getattr(doc, name), name))), 1)
        return


    def FIXMEtestDoctypeInfo(self):
        doc = amara.parse(XSA)
        self.assertEqual(doc.xml_pubid, u'-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML')
        self.assertEqual(doc.xml_sysid, u'http://www.garshol.priv.no/download/xsa/xsa.dtd')
        self.assertEqual(doc.xml_doctype_name, u'xsa')
        return


if __name__ == '__main__':
    unittest.main()

