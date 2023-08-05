#Tests mutation

import unittest
import cStringIO
import amara
from Ft.Xml.Domlette import PrettyPrint
from Ft.Xml.Xslt.XmlWriter import XmlWriter
from Ft.Xml.Xslt.OutputParameters import OutputParameters
from xml.dom import Node


XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'


class TestBasicMods(unittest.TestCase):
    #def setUp(self):
    #    return

    def testBasicCreateDoc1(self):
        EXPECTED = "<A/>"
        doc = amara.create_document(u"A")
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc2(self):
        EXPECTED = '<A xmlns:ns="urn:bogus" ns:a="b"/>'
        doc = amara.create_document(
            u"A", attributes={(u"ns:a", u"urn:bogus"): u"b"})
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc3(self):
        EXPECTED = '<A a="b"/>'
        #Namespace-free attr creation, abbreviated
        doc = amara.create_document(
            u"A", attributes={u"a": u"b"})
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #Namespace-free attr creation, full
        doc = amara.create_document(
            u"A", attributes={(u"a", None): u"b"})
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc4(self):
        doc = amara.create_document(u"A")
        e1 = doc.xml_create_element(u"B", content=u"One",
                             attributes={(u"ns:a", u"urn:bogus"): u"b"})
        doc.A.xml_append(e1)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        EXPECTED = '<A><B xmlns:ns="urn:bogus" ns:a="b">One</B></A>'
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc4(self):
        EXPECTED = '<A><B a="b">One</B></A>'
        #Namespace-free attr creation, abbreviated
        doc = amara.create_document(u"A")
        e1 = doc.xml_create_element(u"B", content=u"One",
                             attributes={u"a": u"b"})
        doc.A.xml_append(e1)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #Namespace-free attr creation, full
        doc = amara.create_document(u"A")
        e1 = doc.xml_create_element(u"B", content=u"One",
                             attributes={(u"a", None): u"b"})
        doc.A.xml_append(e1)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc5(self):
        EXPECTED = '<A a="b"/>'
        doc = amara.create_document(u"A")
        doc.A.a = u"b"
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testBasicCreateDoc6(self):
        EXPECTED = '<A xmlns:ns="urn:bogus" ns:a="b"/>'
        doc = amara.create_document(u"A")
        doc.A.xml_set_attribute((u"ns:a", u"urn:bogus"), u"b")
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testCreateDoc2(self):
        doc = amara.create_document(u"A")
        e1 = doc.xml_create_element(u"A", content=u"One")
        e2 = doc.xml_create_element(u"B", content=u"Two")
        doc.A.xml_append(e1)
        doc.A.xml_append(e2)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(list(doc.A.A)), 1)
        self.assertEqual(len(list(doc.A.B)), 1)
        self.assertEqual(unicode(doc.A.A), u"One")
        self.assertEqual(unicode(doc.A.B), u"Two")
        EXPECTED = "<A><A>One</A><B>Two</B></A>"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        EXPECTED = "<A>\n  <A>One</A>\n  <B>Two</B>\n</A>"
        op = OutputParameters()
        op.indent = u"yes"
        stream = cStringIO.StringIO()
        w = XmlWriter(op, stream)
        doc.xml(writer=w)
        self.assertEqual(stream.getvalue(), XMLDECL+EXPECTED)
        #PrettyPrint(doc)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testCreateDocNs1(self):
        EXPECTED = '<A xmlns="urn:bogus"/>'
        doc = amara.create_document(u"A", u"urn:bogus")
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testTemplate1(self):
        EXPECTED = '<A><B a="b">One</B></A>'
        doc = amara.create_document(u"A")
        doc.A.xml_append_fragment('<B a="b">One</B>')
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testTemplate2(self):
        EXPECTED = '<A><B xmlns:ns="urn:bogus" ns:a="b">One</B></A>'
        doc = amara.create_document(u"A")
        doc.A.xml_append_fragment('<B xmlns:ns="urn:bogus" ns:a="b">One</B>')
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testTemplate3(self):
        EXPECTED = '<A xmlns:ns="urn:bogus" ns:a="b"><B>One</B></A>'
        doc = amara.create_document(u"A", attributes={(u'ns:a', u"urn:bogus"): u'b'})
        doc.A.xml_append_fragment('<B>One</B>')
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testTemplate4(self):
        EXPECTED = '<A><B xmlns:ns="urn:bogus" ns:a="b">One</B></A>'
        doc = amara.create_document(u"A")
        doc.A.xml_append_fragment('<B xmlns:ns="urn:bogus" ns:a="b">One</B>')
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testTemplate5(self):
        EXPECTED = u'<A><B>\u2203</B></A>'.encode('utf-8')
        doc = amara.create_document(u'A')
        doc.A.xml_append_fragment(u'<B>\u2203</B>'.encode('utf-8'))
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testTemplate6(self):
        EXPECTED = u'<A><B>\u00AB\u00BB</B></A>'.encode('utf-8')
        doc = amara.create_document(u'A')
        doc.A.xml_append_fragment(u'<B>\u00AB\u00BB</B>'.encode('latin-1'), 'latin-1')
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return


    def testCreateDocType1(self):
        EXPECTED = '<!DOCTYPE xsa PUBLIC "-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML" "http://www.garshol.priv.no/download/xsa/xsa.dtd">\n<xsa/>'
        doc = amara.create_document(
            u"xsa",
            pubid=u"-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML",
            sysid=u"http://www.garshol.priv.no/download/xsa/xsa.dtd"
            )
        self.assertEqual(len(list(doc.xsa)), 1)
        self.assertEqual(len(doc.xsa.xml_children), 0)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        #PrettyPrint(doc)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testCreateDocType2(self):
        EXPECTED = '<!DOCTYPE xsa PUBLIC "-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML" "http://www.garshol.priv.no/download/xsa/xsa.dtd">\n<xsa/>'
        doc = amara.create_document(
            u"xsa",
            pubid=u"-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML",
            sysid=u"http://www.garshol.priv.no/download/xsa/xsa.dtd"
            )
        self.assertEqual(len(list(doc.xsa)), 1)
        self.assertEqual(len(doc.xsa.xml_children), 0)
        self.assertEqual(doc.xml(indent=u'yes'), XMLDECL+EXPECTED)
        #PrettyPrint(doc)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testCreateDocType4(self):
        EXPECTED = '<!DOCTYPE xsa PUBLIC "-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML" "http://www.garshol.priv.no/download/xsa/xsa.dtd">\n<xsa/>'
        op = OutputParameters()
        op.indent = u'yes'
        op.doctypeSystem = u"http://www.garshol.priv.no/download/xsa/xsa.dtd"
        op.doctypePublic = u"-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML"
        stream = cStringIO.StringIO()
        w = XmlWriter(op, stream)
        doc = amara.create_document(u"xsa")
        self.assertEqual(len(list(doc.xsa)), 1)
        self.assertEqual(len(doc.xsa.xml_children), 0)
        doc.xml(writer=w)
        self.assertEqual(stream.getvalue(), XMLDECL+EXPECTED)
        #PrettyPrint(doc)
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testReplace(self):
        EXPECTED = '<A><B id="1">One</B><B id="2">Two</B></A>'
        DOC = EXPECTED
        doc = amara.parse(DOC)
        del doc.A.B[1]
        e2 = doc.xml_create_element(u"B", content=u"Two",
                             attributes={u"id": u"2"})
        doc.A.xml_append(e2)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def XXXtestRepeatEdits1(self):
        print "testRepeatEdits1"
        #EXPECTED = '<A><B a="b">One</B></A>'
        doc = amara.create_document(u"A")
        e1 = doc.xml_create_element(u"B", content=u"One",
                             attributes={u"a": u"b"})
        doc.A.xml_append(e1)
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(len(doc.A.xml_children), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement1(self):
        DOC = "<a><b>spam</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        doc.a.b = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement2(self):
        DOC = "<a><b>spam</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        doc.a.b[0] = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement3(self):
        DOC = "<a><b>spam</b><b>spam</b></a>"
        EXPECTED = '<a><b>eggs</b><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.b = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement4(self):
        DOC = "<a><b>spam</b><b>spam</b></a>"
        EXPECTED = '<a><b>eggs</b><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.b[0] = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement5(self):
        DOC = "<a><b>spam</b><b>spam</b></a>"
        EXPECTED = '<a><b>spam</b><b>eggs</b></a>'
        doc = amara.parse(DOC)
        doc.a.b[1] = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetChildElement6(self):
        DOC = "<a><b>spam</b><b>spam</b></a>"
        doc = amara.parse(DOC)
        def edit():
            doc.a.b[2] = u"eggs"
        self.assertRaises(IndexError, edit)
        return

    def testDelChildElement1(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        del doc.a.b
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElement2(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        del doc.a.b[0]
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElement3(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>spam</b></a>'
        doc = amara.parse(DOC)
        del doc.a.b[1]
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElement4(self):
        DOC = "<a><b>spam</b><b>spam</b></a>"
        doc = amara.parse(DOC)
        def edit():
            del doc.a.b[2]
        self.assertRaises(IndexError, edit)
        return

    def testDelChildElement5(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        del doc.a[u'b']
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElement6(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>eggs</b></a>'
        doc = amara.parse(DOC)
        del doc.a[u'b'][0]
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElement7(self):
        DOC = "<a><b>spam</b><b>eggs</b></a>"
        EXPECTED = '<a><b>spam</b></a>'
        doc = amara.parse(DOC)
        del doc.a[u'b'][1]
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelChildElementWithClash1(self):
        DOC = '<a-1 b-1=""><b-1/></a-1>'
        EXPECTED = '<a-1 b-1=""/>'
        doc = amara.parse(DOC)
        E = Node.ELEMENT_NODE
        del doc[E, None, u'a-1'][E, None, u'b-1']
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelAttributeWithClash1(self):
        DOC = '<a-1 b-1=""><b-1/></a-1>'
        EXPECTED = '<a-1><b-1/></a-1>'
        doc = amara.parse(DOC)
        E = Node.ELEMENT_NODE
        A = Node.ATTRIBUTE_NODE
        del doc[E, None, u'a-1'][A, None, u'b-1']
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testDelAttribute1(self):
        DOC = '<a b="spam"><b>spam</b></a>'
        EXPECTED = '<a><b>spam</b></a>'
        doc = amara.parse(DOC)
        del doc.a.b
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute1(self):
        DOC = '<a b="spam"></a>'
        EXPECTED = '<a b="eggs"/>'
        doc = amara.parse(DOC)
        doc.a.b = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute2(self):
        DOC = '<a b="spam"><b>spam</b></a>'
        EXPECTED = '<a b="eggs"><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.b = u"eggs"
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute3(self):
        from xml.dom import Node
        DOC = '<a b="spam"><b>spam</b></a>'
        EXPECTED = '<a b="eggs"><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a[Node.ATTRIBUTE_NODE, None, u'b'] = u'eggs'
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute4(self):
        DOC = '<a><b>spam</b></a>'
        EXPECTED = '<a><b xml:lang="en">spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.b.xml_set_attribute((u"xml:lang"), u"en")
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute5(self):
        DOC = '<a><b>spam</b></a>'
        EXPECTED = '<a xmlns:ns="urn:bogus" ns:foo="bar"><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.xml_set_attribute((u"ns:foo", u"urn:bogus"), u"bar")
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute6(self):
        DOC = '<a><b>spam</b></a>'
        EXPECTED = '<a xmlns:ns="urn:bogus" ns:foo="bar"><b>spam</b></a>'
        doc = amara.parse(DOC, prefixes={u'ns': u'urn:bogus'})
        doc.a.xml_set_attribute((u"foo", u"urn:bogus"), u"bar")
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testSetAttribute7(self):
        DOC = '<a><b>spam</b></a>'
        EXPECTED = '<a foo="bar"><b>spam</b></a>'
        doc = amara.parse(DOC)
        doc.a.xml_set_attribute(u"foo", u"bar")
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testInsertAfter1(self):
        DOC = "<a><b>spam</b></a>"
        EXPECTED = '<a><b>spam</b><b>eggs</b></a>'
        doc = amara.parse(DOC)
        doc.a.xml_insert_after(doc.a.b, doc.a.xml_create_element(u'b', content=u"eggs"))
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testInsertAfter2(self):
        DOC = "<a><b>spam</b></a>"
        EXPECTED = '<a><b>spam</b><c>eggs</c></a>'
        doc = amara.parse(DOC)
        doc.a.xml_insert_after(doc.a.b, doc.a.xml_create_element(u'c', content=u"eggs"))
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testInsertAfter3(self):
        DOC = "<a><b>spam</b><c>ham</c><c>pork</c></a>"
        EXPECTED = "<a><b>spam</b><c>eggs</c><c>ham</c><c>pork</c></a>"
        doc = amara.parse(DOC)
        doc.a.xml_insert_after(doc.a.b, doc.a.xml_create_element(u'c',
                                                     content=u'eggs'))
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testInsertBefore1(self):
        DOC = "<a><b>eggs</b></a>"
        EXPECTED = '<a><b>spam</b><b>eggs</b></a>'
        doc = amara.parse(DOC)
        doc.a.xml_insert_before(doc.a.b, doc.a.xml_create_element(u'b', content=u"spam"))
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return


MONTY = """\
<?xml version="1.0" encoding="utf-8"?>
<monty>
  <python spam="eggs">
    What do you mean "bleh"
  </python>
  <python ministry="abuse">
    But I was looking for argument
  </python>
</monty>
"""


class TestTransforms(unittest.TestCase):
    def testDeepCopy(self):
        #FIXME really goes in manual.py, since it's based on a manual example
        EXPECTED1 = '<python spam="eggs">\n    What do you mean "bleh"\n  </python>'
        EXPECTED2 = '<python spam="abcd">\n    What do you mean "bleh"\n  </python>'
        import copy
        doc = amara.parse(MONTY)
        doc2 = copy.deepcopy(doc)
        doc2.monty.python.spam = u"abcd"

        self.assertEqual(doc.monty.python.xml(), EXPECTED1)
        self.assertEqual(doc2.monty.python.xml(), EXPECTED2)
        return


if __name__ == '__main__':
    unittest.main()

