#Tests mutation

import unittest
import cStringIO
from xml.dom import Node

import amara
from amara import bindery
from Ft.Xml.Domlette import PrettyPrint
from Ft.Xml.Xslt.XmlWriter import XmlWriter
from Ft.Xml.Xslt.OutputParameters import OutputParameters


XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

ROOT_GI_IN_CHILD = """\
<A>
  <A>One</A>
  <B>Two</B>
</A>
"""

PI_PRE_DOCTYPE = """\
<!DOCTYPE xsa PUBLIC
"-//LM Garshol//DTD XML Software Autoupdate 1.0//EN//XML"
"http://www.garshol.priv.no/download/xsa/xsa.dtd">
<?xml-stylesheet href="xxx.css" type="text/css"?>
<xsa/>"""

TOP_PI = """\
<?xml-stylesheet href="xxx.css" type="text/css"?>
<hello/>"""

TOP_COMMENT = """\
<!--A greeting for all-->
<hello/>"""

TOP_PI_COMMENT = """\
<?xml-stylesheet href="xxx.css" type="text/css"?>
<!--A greeting for all-->
<hello/>"""

COMMENT = """\
<hello><!--A greeting for all--></hello>"""

PI = """\
<hello><?hello world?></hello>"""

PI_COMMENT = """\
<hello><?hello world?><!--A greeting for all--></hello>"""


class TestPisComments(unittest.TestCase):

    def testParseTopPi(self):
        doc = amara.parse(TOP_PI)
        pi = doc.xml_children[0]
        self.assertEqual(len(doc.xml_children), 2)
        self.assertEqual(pi.target, u'xml-stylesheet')
        self.assertEqual(pi.data, u'href="xxx.css" type="text/css"')
        self.assertEqual(len(doc.xml_xpath(u'//node()')), 2)
        self.assertEqual(doc.xml_xpath(u'//node()')[0].nodeType, Node.PROCESSING_INSTRUCTION_NODE)
        self.assertEqual(len(doc.xml_xpath(u'//processing-instruction()')), 1)
        return

    def testParseTopComment(self):
        binder = bindery.binder()
        binder.preserve_comments = True
        doc = amara.parse(TOP_COMMENT, binderobj=binder)
        comment = doc.xml_children[0]
        self.assertEqual(len(doc.xml_children), 2)
        self.assertEqual(comment.data, u'A greeting for all')
        self.assertEqual(len(doc.xml_xpath(u'//node()')), 2)
        self.assertEqual(doc.xml_xpath(u'//node()')[0].nodeType, Node.COMMENT_NODE)
        self.assertEqual(len(doc.xml_xpath(u'//comment()')), 1)
        return

    def testParseTopPiComment(self):
        binder = bindery.binder()
        binder.preserve_comments = True
        doc = amara.parse(TOP_PI_COMMENT, binderobj=binder)
        pi = doc.xml_children[0]
        comment = doc.xml_children[1]
        #print doc.xml_children
        self.assertEqual(len(doc.xml_children), 3)
        self.assertEqual(pi.target, u'xml-stylesheet')
        self.assertEqual(pi.data, u'href="xxx.css" type="text/css"')
        self.assertEqual(comment.data, u'A greeting for all')
        EXPECTED = '<?xml-stylesheet href="xxx.css" type="text/css"?><!--A greeting for all--><hello/>'
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)

        #XPath
        self.assertEqual(len(doc.xml_xpath(u'//node()')), 3)
        self.assertEqual(doc.xml_xpath(u'//node()')[0].nodeType, Node.PROCESSING_INSTRUCTION_NODE)
        self.assertEqual(doc.xml_xpath(u'//node()')[1].nodeType, Node.COMMENT_NODE)
        self.assertEqual(len(doc.xml_xpath(u'//processing-instruction()')), 1)
        self.assertEqual(len(doc.xml_xpath(u'//comment()')), 1)
        return

    def testParsePi(self):
        doc = amara.parse(PI)
        elem = doc.xml_children[0]
        pi = elem.xml_children[0]
        self.assertEqual(len(doc.xml_children), 1)
        self.assertEqual(pi.target, u'hello')
        self.assertEqual(pi.data, u'world')
        self.assertEqual(len(doc.xml_xpath(u'//node()')), 2)
        self.assertEqual(doc.xml_xpath(u'//node()')[1].nodeType, Node.PROCESSING_INSTRUCTION_NODE)
        self.assertEqual(len(doc.xml_xpath(u'//processing-instruction()')), 1)
        return

    def testParseComment(self):
        binder = bindery.binder()
        binder.preserve_comments = True
        doc = amara.parse(COMMENT, binderobj=binder)
        elem = doc.xml_children[0]
        comment = elem.xml_children[0]
        self.assertEqual(len(doc.xml_children), 1)
        self.assertEqual(comment.data, u'A greeting for all')
        self.assertEqual(len(doc.xml_xpath(u'//node()')), 2)
        self.assertEqual(doc.xml_xpath(u'//node()')[0].nodeType, Node.COMMENT_NODE)
        self.assertEqual(len(doc.xml_xpath(u'//comment()')), 1)
        self.assertEqual(len(elem.xml_children), 1)
        self.assertEqual(unicode(elem), '')
        return

    def testCreateDocPi1(self):
        EXPECTED = '<?xml-stylesheet href="xxx.css" type="text/css"?><A/>'
        doc = amara.create_document()
        pi = bindery.pi_base(u"xml-stylesheet", u'href="xxx.css" type="text/css"')
        doc.xml_append(pi)
        doc.xml_append(doc.xml_create_element(u"A"))
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return

    def testCreateDocPi2(self):
        EXPECTED = '<?xml-stylesheet href="xxx.css" type="text/css"?>\n<A/>'
        doc = amara.create_document()
        pi = bindery.pi_base(u"xml-stylesheet", u'href="xxx.css" type="text/css"')
        doc.xml_append(pi)
        doc.xml_append(doc.xml_create_element(u"A"))
        op = OutputParameters()
        op.indent = u"yes"
        stream = cStringIO.StringIO()
        w = XmlWriter(op, stream)
        doc.xml(writer=w)
        self.assertEqual(stream.getvalue(), XMLDECL+EXPECTED)
        return
        EXPECTED = "<A>\n  <A>One</A>\n  <B>Two</B>\n</A>"
        #
        #self.assert_(isinstance(doc.xbel.title, unicode))
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testCreateDocPi3(self):
        EXPECTED = '<?xml-stylesheet href="xxx.css" type="text/css"?>\n<A/>\n'
        doc = amara.create_document()
        pi = bindery.pi_base(u"xml-stylesheet", u'href="xxx.css" type="text/css"')
        doc.xml_append(pi)
        doc.xml_append(doc.xml_create_element(u"A"))
        self.assertEqual(len(list(doc.A)), 1)
        stream = cStringIO.StringIO()
        PrettyPrint(doc, stream=stream)
        self.assertEqual(stream.getvalue(), XMLDECL+EXPECTED)
        return

    def testCreateDocComment1(self):
        EXPECTED = '<!--Test comment--><A/>'
        doc = amara.create_document()
        comment = bindery.comment_base(u"Test comment")
        doc.xml_append(comment)
        doc.xml_append(doc.xml_create_element(u"A"))
        self.assertEqual(len(list(doc.A)), 1)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        return


if __name__ == '__main__':
    unittest.main()

