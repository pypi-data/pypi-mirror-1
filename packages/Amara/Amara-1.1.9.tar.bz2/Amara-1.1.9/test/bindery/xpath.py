#Tests bindery rules

import unittest
import amara

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

RSS = """\
<?xml version="1.0"?>
<rdf:RDF 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
  xmlns="http://purl.org/rss/1.0/"
> 

  <channel rdf:about="http://meerkat.oreillynet.com/">
    <title>Meerkat: An Open Wire Service</title> 
    <link>http://meerkat.oreillynet.com/</link> 
    <description>
      This Meerkat flavour, rss10, conforms to the current status of
      RSS 1.0 development.  Please note that it may change at any time.
    </description>
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>2</sy:updateFrequency>
    <sy:updateBase>2000-01-01T12:00+00:00</sy:updateBase>

    <image rdf:resource="http://meerkat.oreillynet.com/icons/meerkat-powered.jpg" />

    <items>
      <rdf:Seq>
        <rdf:li rdf:resource="http://www.oreillynet.com/cs/weblog/view/wlg/536" />
        <rdf:li rdf:resource="http://www.oreillynet.com/cs/weblog/view/wlg/534" />
      </rdf:Seq>
    </items>
  
    <textinput rdf:resource="http://meerkat.oreillynet.com/#search" />

  </channel>

  <image rdf:about="http://meerkat.oreillynet.com/icons/meerkat-powered.jpg">
    <title>Meerkat Powered!</title>
    <url>http://meerkat.oreillynet.com/icons/meerkat-powered.jpg</url>
    <link>http://meerkat.oreillynet.com</link>
  </image>

  <item rdf:about="http://www.oreillynet.com/cs/weblog/view/wlg/536">
    <title>Learn Java in 14 Lines! by Frank Willison</title>
    <link>http://www.oreillynet.com/cs/weblog/view/wlg/536</link>
    <description> In Memory of Frank Willison, O&#039;Reilly Editor in Chief, we find his take on learning Java with a sample tutorial sonnet, &amp;quot;Alas! I Married a Java Applet!,&amp;quot; from his Learn Java in 14 Lines!. </description>
    <dc:source>O&#039;Reilly Network Weblogs</dc:source>
    <dc:creator>Steve Anglin</dc:creator>
    <dc:subject>Java</dc:subject>
    <dc:publisher>O'Reilly and Associates</dc:publisher>
    <dc:date>2001-08-02 10:42:42</dc:date>
    <dc:format>text/html</dc:format>
    <dc:language>en-us</dc:language>
    <dc:rights>Copyright 2001, O'Reilly and Associates</dc:rights>
  </item>

  <item rdf:about="http://www.oreillynet.com/cs/weblog/view/wlg/534">
    <title>IBM joins push to construct next-generation internet</title>
    <link>http://www.oreillynet.com/cs/weblog/view/wlg/534</link>
    <description> The movement to build a new-generation internet through a global computer &amp;quot;grid&amp;quot; will receive a big boost on Thursday when International Business Machines, the world&#039;s largest computing company, commits itself to the new technology. </description>
    <dc:source>O&#039;Reilly Network Weblogs</dc:source>
    <dc:creator>John Scott</dc:creator>
    <dc:subject>P2P</dc:subject>
    <dc:publisher>O'Reilly and Associates</dc:publisher>
    <dc:date>2001-08-02 07:20:52</dc:date>
    <dc:format>text/html</dc:format>
    <dc:language>en-us</dc:language>
    <dc:rights>Copyright 2001, O'Reilly and Associates</dc:rights>
  </item>

</rdf:RDF>
"""

class TestXPath(unittest.TestCase):
    #def setUp(self):
    #    return

    def testAttrAxis1(self):
        doc = amara.parse(LABELS)
        self.assert_(hasattr(doc.labels.label, "xml_attributes"))
        self.assertEqual(len(list(doc.labels)), 1)
        self.assertEqual(len(list(doc.labels.label)), 4)
        self.assertEqual(len(list(doc.labels.label.name)), 1)
        self.assertEqual(len(list(doc.labels.label.address)), 1)
        self.assertEqual(len(list(doc.labels.label.address.city)), 1)
        self.assertEqual(len(list(doc.labels.label.address.street)), 1)
        self.assertEqual(len(list(doc.labels.label.address.province)), 1)
        self.assertEqual(doc.xml_xpath(u"count(//@id)"), 4.0)
        self.assertEqual(doc.xml_xpath(u"count(//@*)"), 8.0)
        self.assertEqual(doc.xml_xpath(u"string(/labels/label[@id='ep']/name)"), u"Ezra Pound")
        return

    def testAttrAxis2(self):
        XML = '<html><test href="bar" /><test href="foo" /></html>'
        doc = amara.parse(XML)
        self.assertEqual(doc.xml_xpath(u"count(//@href)"), 2.0)
        self.assert_([ a.value for a in doc.xml_xpath(u"//@href")] in [[u"foo", u"bar"], [u"bar", u"foo"]])
        self.assertEqual(doc.xml_xpath(u"count(//@href|//@bogus)"), 2.0)
        self.assert_([ a.value for a in doc.xml_xpath(u"//@href|//@bogus")] in [[u"foo", u"bar"], [u"bar", u"foo"]])
        return

    def testAttrAxisNs(self):
        RSS10_NSS = {
            u'rdf': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            u'dc': u'http://purl.org/dc/elements/1.1/',
            u'rss': u'http://purl.org/rss/1.0/',
            }
        doc = amara.parse(RSS, prefixes=RSS10_NSS)
        self.assert_(not hasattr(doc.RDF, "xml_attributes"))
        self.assert_(hasattr(doc.RDF.channel, "xml_attributes"))
        self.assertEqual(len(list(doc.RDF)), 1)
        self.assertEqual(doc.xml_xpath(u"count(//@rdf:about)"), 4.0)
        self.assertEqual(doc.xml_xpath(u"count(//rss:item/@rdf:about)"), 2.0)
        self.assertEqual(doc.xml_xpath(u"count(//@rdf:resource)"), 4.0)
        self.assertEqual(doc.xml_xpath(u"count(//rdf:li/@rdf:resource)"), 2.0)
        self.assertEqual(
            doc.xml_xpath(u"string(//rss:item[@rdf:about='http://www.oreillynet.com/cs/weblog/view/wlg/534']/rss:title)"), u"IBM joins push to construct next-generation internet"
            )
        return

if __name__ == '__main__':
    unittest.main()

