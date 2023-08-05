#Tests bindery rules

import unittest
import datetime
import amara
from amara import binderytools

LABELS = """\
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

XBEL = """\
<?xml version="1.0" encoding="utf-8"?>
<!--
<!DOCTYPE xbel PUBLIC "+//IDN python.org//DTD XML Bookmark Exchange Language 1.0//EN//XML" "http://www.python.org/topics/xml/dtds/xbel-1.0.dtd">
-->
<xbel>
  <title>Some 4Suite Bookmarks</title>
  <!-- No top level bookmars -->
  <folder>
    <title>Main links</title>
    <bookmark href="http://4suite.org/">
      <title>4Suite home page</title>
    </bookmark>
    <bookmark href="http://foursuite.sourceforge.net/">
      <title>4Suite on SourceForge</title>
    </bookmark>
    <bookmark href="http://uche.ogbuji.net/tech/4Suite/">
      <title>Uche's 4Suite page</title>
    </bookmark>
    <bookmark href="http://twistedmatrix.com/users/jh.twistd/xml-sig/moin.cgi/FtSuiteWiki">
      <title>4Suite Wiki</title>
    </bookmark>
  </folder>
  <folder>
    <title>Articles</title>
    <bookmark href="http://www.xml.com/pub/a/2002/10/16/py-xml.html">
      <title>Python &amp; XML: A Tour of 4Suite</title>
    </bookmark>
    <folder>
      <title>Free registration required</title>
      <bookmark href="http://www-105.ibm.com/developerworks/education.nsf/xml-onlinecourse-bytitle/BE1A7E60838F9F7686256AF400523C58">
        <title>Python and XML development using 4Suite, Part 2: 4XPath and 4XSLT </title>
      </bookmark>
      <bookmark href="http://www-105.ibm.com/developerworks/education.nsf/xml-onlinecourse-bytitle/8A1EA5A2CF4621C386256BBB006F4CEC">
        <title>Python and XML development using 4Suite, Part 3: 4RDF</title>
      </bookmark>
      <bookmark href="http://www-105.ibm.com/developerworks/education.nsf/xml-onlinecourse-bytitle/CD1A8865668D9A2E86256C910062D445?OpenDocument">
        <title>Develop Python/XML with 4Suite, Part 5: The Repository Features</title>
      </bookmark>
    </folder>
  </folder>
  <folder>
    <title>Mailing lists</title>
    <bookmark href="http://lists.fourthought.com/mailman/listinfo/4suite">
      <title>4Suite Mailing List</title>
    </bookmark>
    <bookmark href="http://lists.fourthought.com/mailman/listinfo/4suite-ann">
      <title>4Suite Announcements Mailing List</title>
    </bookmark>
    <bookmark href="http://lists.fourthought.com/mailman/listinfo/4suite-dev">
      <title>4Suite Developer Mailing List</title>
    </bookmark>
  </folder>
</xbel>
"""

TYPE_MIX = """\
<?xml version="1.0" encoding="utf-8"?>
<a a1="1">
  <b b1="2.1"/>
  <b>3</b>
  <c c1="2005-01-31">
    <d>5</d>
    <e>2003-01-30T17:48:07.848769Z</e>
    <!--e>2003-01-30T17:48:07.848769</e--> <!-- Doesn't work right now without any TZ info (e.g. 'Z') -->
  </c>
  <g>good</g>
</a>
"""

class TestRules(unittest.TestCase):
    #def setUp(self):
    #    return

    def testMultipleSimpleStringRules(self):
        #patterns = [u'name', u'address/street', u'address/city',
        #            '/labels/label/address/province']
        #rules = [ binderytools.simple_string_element_rule(p) for p in patterns ]
        patterns = [u'bookmark/title', u'xbel/title']
        rules = [ binderytools.simple_string_element_rule(p) for p in patterns ]
        doc = amara.parse(XBEL, rules=rules)
        self.assert_(isinstance(doc.xbel.title, unicode))
        self.assert_(isinstance(doc.xbel.folder.bookmark.title, unicode))
        self.assert_(not(isinstance(doc.xbel.folder.title, unicode)))
        self.assertEqual(doc.xbel.title, u'Some 4Suite Bookmarks')
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testMultipleOmitElementRules(self):
        patterns = [u'folder/title', u'xbel/title']
        rules = [ binderytools.omit_element_rule(p) for p in patterns ]
        doc = amara.parse(XBEL, rules=rules)
        self.assertEquals(unicode(doc.xbel.folder.bookmark.title), u"4Suite home page")
        #Yeah, could just do assert_(hasattr but this way I remember how assertRaises works
        #Consider assertRaisesEx from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/307970
        self.assertRaises(AttributeError, lambda x=None: doc.xbel.title)
        self.assertRaises(AttributeError, lambda x=None: doc.xbel.folder.title)
        return

    def testSimpleAndOmitRules(self):
        rules = [
            binderytools.omit_element_rule(u'folder/title'),
            binderytools.omit_element_rule(u'xbel/title'),
            binderytools.simple_string_element_rule(u'bookmark/title')
            ]
        doc = amara.parse(XBEL, rules=rules)
        self.assert_(isinstance(doc.xbel.folder.bookmark.title, unicode))
        self.assertEquals(doc.xbel.folder.bookmark.title, u"4Suite home page")
        #Yeah, could just do assert_(hasattr but this way I remember how assertRaises works
        #Consider assertRaisesEx from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/307970
        self.assertRaises(AttributeError, lambda x=None: doc.xbel.title)
        self.assertRaises(AttributeError, lambda x=None: doc.xbel.folder.title)
        return

    def testTypeInference(self):
        rules = [ binderytools.type_inference(u"*") ]
        doc = amara.parse(TYPE_MIX, rules=rules)
        self.assertEqual(doc.a.a1, 1)
        self.assertEqual(doc.a.b.b1, 2.1)
        try:
            from dateutil.tz import tzlocal
            #self.assertEqual(doc.a.c.c1, datetime.datetime.now(tzlocal()))
            self.assertEqual(doc.a.c.c1, datetime.datetime(2005, 1, 31, tzinfo=tzlocal()))
            #Because of timezone conversion with have to check within 24 hrs (86400 seconds)
            self.assert_(doc.a.c.e - datetime.datetime(2003, 1, 30, 17, 48, 7, 848769, tzinfo=tzlocal()) < datetime.timedelta(0, 86400))
        except ImportError:
            self.assertEqual(doc.a.c.c1, datetime.datetime(2005, 1, 31))
            #Because of timezone conversion with have to check within 24 hrs (86400 seconds)
            self.assert_(doc.a.c.e - datetime.datetime(2003, 1, 30, 17, 48, 7, 848769) < datetime.timedelta(0, 86400))
        #self.assertEqual(len(list(doc.labels)), 1)
        #self.assertEqual(doc.xml_xpath(u"count(//@id)"), 4.0)
        return

    def testWhitespaceStripping1(self):
        rules = [ binderytools.ws_strip_element_rule(u"*") ]
        doc = amara.parse("<a>  <b/>  </a>", rules=rules)
        #print [ l.id for l in doc.labels.label ]
        #self.assertEqual(len(list(doc.labels.label)), 4)
        self.assertEqual(len(doc.a.xml_children), 1)
        #self.assertEqual(doc.xml_xpath(u"count(//@id)"), 4.0)
        return

    def testWhitespaceStripping4(self):
        rules = [ binderytools.ws_strip_element_rule(u"*") ]
        doc = amara.parse(LABELS, rules=rules)
        #print [ l.id for l in doc.labels.label ]
        #self.assertEqual(len(list(doc.labels.label)), 4)
        self.assertEqual(len(doc.labels.xml_children), 4)
        #self.assertEqual(doc.xml_xpath(u"count(//@id)"), 4.0)
        return

    def testElementSkeletonRule1(self):
        rules = [
            binderytools.element_skeleton_rule(u'label'),
            ]
        doc = amara.parse(LABELS, rules=rules)
        self.assertEquals(len(doc.labels.label.name.childNodes), 0)
        self.assertEquals(len(doc.labels.label[1].name.childNodes), 0)
        self.assertEquals(len(doc.labels.label[2].name.childNodes), 0)
        self.assertEquals(len(doc.labels.label.address.street.childNodes), 0)
        self.assertEquals(len(doc.labels.label[1].address.street.childNodes), 0)
        self.assertEquals(len(doc.labels.label[2].address.street.childNodes), 0)
        self.assertEquals(len(doc.labels.label.address.city.childNodes), 0)
        return

    def testElementSkeletonRule2(self):
        rules = [
            binderytools.element_skeleton_rule(u'folder'),
            ]
        doc = amara.parse(XBEL, rules=rules)
        self.assertEquals(len(doc.xbel.title.childNodes), 1)
        self.assertEquals(len(doc.xbel.folder.title.childNodes), 0)
        self.assertEquals(len(doc.xbel.folder[1].title.childNodes), 0)
        self.assertEquals(len(doc.xbel.folder[1].folder.title.childNodes), 0)
        return


if __name__ == '__main__':
    unittest.main()

