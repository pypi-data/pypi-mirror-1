# -*- coding: utf-8 -*-
#Tests examples given in the manual

import unittest
import amara
from amara import binderytools
from Ft.Xml import InputSource
from Ft.Lib import Uri


class TestBase(unittest.TestCase):
    def setUp(self):
        self.isrc_factory = InputSource.DefaultFactory
        return

    def _input_source_for_file(self, fname):
        #Create a URI from a filename the right way
        file_uri = Uri.OsPathToUri(fname, attemptAbsolute=1)
        isrc = self.isrc_factory.fromUri(file_uri)
        return isrc

    def _input_source_for_string(self, text, uri="urn:bogus:dummy"):
        isrc = self.isrc_factory.fromString(text, uri)
        return isrc


class TestMJ030815(TestBase):
    XML = """\
<birds country='germany' >
    <raptor endangered='yes' wingspan='240cm'>
        <english_name>White-tailed Eagle</english_name>
        <german_name>Seeadler</german_name>
        <prey>birds</prey>
        <prey>fish</prey>
    </raptor>
    <raptor endangered='no' wingspan='80cm'>
        <english_name>Kestrel</english_name>
        <german_name>Turmfalke</german_name>
        <prey>mice</prey>
    </raptor>
</birds>
"""
    
    def testSpuriousPrints(self):
        #isrc = self._input_source_for_string(self.XML)
        #binder = anobind.binder()
        #binding = binder.read_xml(isrc)
        binding = amara.parse(self.XML)

        output = []
        for raptor in binding.birds.raptor:
            output.append(raptor.wingspan)
            output.append(unicode(raptor.german_name))

        for raptor in binding.xml_xpath(u'/birds/raptor'):
            output.append(raptor.wingspan)
            output.append(unicode(raptor.german_name))

        self.assertEqual(output, [u'240cm', u'Seeadler', u'80cm', u'Turmfalke', u'240cm', u'Seeadler', u'80cm', u'Turmfalke'])
        return


class TestMI030914(TestBase):
    #From private message, sender's name withheld
    XML = """\
<?xml version="1.0" encoding="UTF-8" ?> 
<p1:spokeBookEntry p2:type="p1:SpokeBookEntryType" nonVcf="true" isInvited="false" isSuppressed="false" href="/member/510379/spokebook/512367" inPrivacyFence="false" privacyLevel="public" xmlns:p1="http://ns.spoke.com/namespace/platform/1.0" xmlns:p2="http://www.w3.org/2001/XMLSchema-instance">
  <p1:person href="/person/512373" /> 
  <p1:sor>26.21035385131836</p1:sor> 
  <p1:sorDelta>0</p1:sorDelta>
  <p1:firstName>Max</p1:firstName> 
  <p1:lastName>Moolah</p1:lastName> 
  <p1:job p2:type="p1:Job" jobID="5866450" isPrimary="true">
    <p1:company href="/company/18711" /> 
    <p1:jobTitle>Chief Executive Officer</p1:jobTitle> 
    <p1:companyName>Juggernaut Holdings</p1:companyName> 
  </p1:job>
  <p1:job p2:type="p1:Job" jobID="421504" isPrimary="false">
    <p1:company href="/company/18711" /> 
    <p1:jobTitle /> 
    <p1:companyName>The Domi Nation, PLC</p1:companyName> 
  </p1:job>
  <p1:address p2:type="p1:StreetAddress" locationID="850151" for="home">
    <p1:state /> 
    <p1:postCode>94403</p1:postCode> 
  </p1:address>
</p1:spokeBookEntry>
"""
 
    def testSimpleLoops(self):
        prefixes = {
            'p1': 'http://ns.spoke.com/namespace/platform/1.0'
            }
        doc = amara.parse(self.XML, prefixes=prefixes)
        #isrc = self._input_source_for_string(self.XML)
        #binder = anobind.binder(namespaces=namespaces)
        #doc = binder.read_xml(isrc)

        output = []
        for r in doc.spokeBookEntry:
            output.append(unicode(r.firstName))
            output.append(unicode(r.lastName))

        for r in doc.spokeBookEntry.xml_xpath(u'p1:job'):
            output.append(unicode(r.companyName))

        self.assertEqual(output, [u'Max', u'Moolah', u'Juggernaut Holdings', u'The Domi Nation, PLC'])
        #self.assertEqual(output, [u'Mary', u'Walker', u'Satmetrix', u'CustomerCast'])
        return

class TestTL030315(TestBase):
    #From Tom Lazar
    def testPiSerialize(self):
        XML = """\
<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/css"  
href="../css/services.css"?>
<!--
<!DOCTYPE services
   PUBLIC "- -//tomster.org//DTD Services//DE" "file:../dtd/services.dtd">
   -->
<services>
  <client id="1021">
    <service billing-id="1314" location="self" performer="tomster" type="isp">
      <description>...</description>
        <date>2005-01-31</date>
        <count>3</count>
        <amount>2.00</amount>
      </service>
      [...]
  </client>
</services>
"""

        EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/css"  \nhref="../css/services.css"?><!--\n<!DOCTYPE services\n   PUBLIC "- -//tomster.org//DTD Services//DE" "file:../dtd/services.dtd">\n   --><services>\n  <client id="1021">\n    <service performer="tomster" type="isp" location="self" billing-id="1314">\n      <description>...</description>\n        <date>2005-01-31</date>\n        <count>3</count>\n        <amount>2.00</amount>\n      </service>\n      [...]\n  </client>\n</services>'
        doc = amara.parse(XML)
        self.assertEqual(doc.xml(), EXPECTED)
        return


class TestTL030315(TestBase):
    #From Tom Lazar
    def testMerge(self):
        XML = """\
<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/css" href="../css/services.css"?>
<!--
<!DOCTYPE services PUBLIC "- -//tomster.org//DTD Services//DE" "file:../dtd/services.dtd">
-->
<services>
  <client id="1023">
    <service billing_id="2" performer="tomster" type="travel" location="client">
      <description>ausserhalb Berlins</description>

      <date>2005-03-04</date>

      <count>1</count>

      <amount>36</amount>
    </service>

    <service billing_id="2" performer="tomster" type="workunit" location="client">
      <description>Umbau Serverplatte in G4 mit funktionierendem optischem
      Laufwerk, Neuvergabe Adminpasswort, Umzug der Rechenanlage in Wattstr.
      17, Aufbau und Test dort</description>

      <date>2005-03-04</date>

      <count>24</count>

      <amount>10</amount>
    </service>

    <service billing_id="2" performer="tomster" type="admin" location="client">
      <description>Telefonsupport</description>

      <date>2005-03-26</date>

      <count>1</count>

      <amount>10</amount>
    </service>
  </client>

  <client id="1035">
    <service billing_id="1" performer="tomster" type="isp" location="self">
      <description>Domainhosting für die domain <b>am-viscom.de</b> für den
      Zeitraum vom 31.9.2004 bis 31.12.2004</description>

      <date>2005-01-31</date>

      <count>3</count>

      <amount>2.00</amount>
    </service>

    <service billing_id="1" performer="tomster" type="isp" location="self">
      <description>500 Mb Speicherplatz für <b>annette</b> für den Zeitraum
      vom 31.9.2004 bis 31.12.2004</description>

      <date>2005-01-31</date>

      <count>3</count>

      <amount>5</amount>
    </service>

    <service billing_id="1" performer="tomster" type="isp" location="self">
      <description>IMAP Dienst inkl. täglichem Backup für das Konto
      <b>annette</b> für den Zeitraum vom 31.9.2004 bis
      31.12.2004</description>

      <date>2005-01-31</date>

      <count>3</count>

      <amount>5.00</amount>
    </service>

    <service billing_id="1" performer="tomster" type="isp" location="self">
      <description>100 Mb Speicherplatz für <b>loic</b> für den Zeitraum vom
      31.9.2004 bis 31.12.2004</description>

      <date>2005-01-31</date>

      <count>3</count>

      <amount>1</amount>
    </service>

    <service billing_id="0" performer="tomster" type="webdev" location="self">
      <description>IMAP Dienst inkl. täglichem Backup für das Konto
      <b>loic</b> für den Zeitraum vom 31.9.2004 bis 31.12.2004</description>

      <date>2005-01-31</date>

      <count>3</count>

      <amount>5.00</amount>
    </service>
  </client>

<client id="1063">
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>Router zurückgesetzt, RAM-Bestellung abgewickelt, backups
      überprüft</description>
      <date>2005-02-02</date>
      <count>0,5</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>G5 iMac komplett neu eingerichtet; Benutzer übertragen,
      diverse Programme installiert, Schriften, Drucker; Druckerproblem
      Xerox/Archifile A3 behoben; Farbkopierer Varianten kurz durchgesprochen,
      Mailimport begonnen; Powerbook G4 komplett neuinstallliert wegen
      DongleProblem LazyJack; funktioniert nun; Benutzer übertragen, Drucker
      und Programme nachinstalliert</description>
      <date>2005-02-09</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>ap 22 Adobe Suite installiert, diverse Programme, Mail
      importiert, Adressen importiert</description>
      <date>2005-02-10</date>
      <count>1,5</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>ag Mail repariert, ap22 Plotter nachinstalliert, Programme
      installiert, 2 iMacs Festplatten ausgetauscht, 3 Systemupdates
      (ap20-22), Druckproblem archifile behoben (hpLJ Buero), 2 x RAM
      installiert</description>
      <date>2005-02-16</date>
      <count>4,2</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>Systemupdates 10.3.8 eingespielt 3 Maschinen,
      Securityupdate 2005-002 eingespielt auf 7 Maschinen, FontShop wegen
      Schriftenproblem kontaktiert, ap21 Rechteproblem behoben, Renderingfrage
      geklärt, ap20 Keynote, Entsorgung der Monitore besprochen, backups
      überprüft, ap9, ap20 Software nachinstalliert (Office)</description>
      <date>2005-02-23</date>
      <count>2,75</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>3 Rechner rechte repariert/Acrobat-Problem behoben,
      Zugriffsrechte für "Projekte ausgelagert" auf dem server geändert,
      Backupset 20GB-Spiegel wegen Platzproblemen angepaßt, Test-Rückspielung
      eine Files aus backupset zur Kontrolle mit Überprüfung (Start der
      LazyJack-Datenbank von der wiederhergestellten Datei)</description>
      <date>2005-02-34</date>
      <count>2,5</count>
      <amount>50</amount>
    </service>
  </client>
  <client id="2055">
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>111111</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>2222222</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>3333</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>44444</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>55555</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>666666</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
    <service billing_id="0" performer="ekke" type="admin" location="client">
      <description>777777</description>
      <date>2005-02-66</date>
      <count>6</count>
      <amount>50</amount>
    </service>
  </client>
</services>"""

        EXPECTED = ''
        doc1 = amara.parse(XML)
        doc2 = amara.parse(XML)
        #self.assertEqual(doc.xml(), EXPECTED)
        for client in doc1.services.client:
            for service_node in client.service:
                doc2.services.client.xml_append(service_node)
        return

XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

class TestJN050418(TestBase):
    #From Jamie Norrish
    def getEntryList(self, doc):
        entryList = []
        for entry in doc.entries.entry:
            entryList.append(unicode(entry))
        return entryList

    def removeEntryByID(self, doc, entryID):
        entry = doc.entries.xml_xpath('entry[@id="%s"]' % unicode(entryID))[0]
        #index = entry.xml_index_on_parent()
        doc.entries.xml_remove_child(entry)

    def makeEntry(self, param):
        doc = amara.create_document()
        doc.xml_append(doc.xml_create_element(u'entry',
                                       attributes={'id': unicode(param)}))
        doc.entry.xml_children.append(unicode(param))
        return doc.entry

    def testRepeatedReplace(self):
        EXPECTED = '<entries><entry id="entry1">entry1</entry><entry id="entry2">entry2</entry></entries>'
        doc = amara.parse('<entries></entries>')
        entry1 = self.makeEntry(u'entry1')
        entry2 = self.makeEntry(u'entry2')
        doc.entries.xml_append(entry1)
        doc.entries.xml_append(entry2)
        self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
        self.assertEqual(self.getEntryList(doc), [u'entry1', u'entry2'])
        for i in range(3):
            entry = self.makeEntry(u'entry2')
            self.removeEntryByID(doc, u'entry2')
            doc.entries.xml_append(entry)
            #self.assertEqual(doc.)
            #self.assertEqual(doc.)
            self.assertEqual(doc.xml(), XMLDECL+EXPECTED)
            self.assertEqual(self.getEntryList(doc), [u'entry1', u'entry2'])

class TestJN050418_1(TestJN050418):
    #First simplification of makeEntry
    def makeEntry(self, param):
        doc = amara.create_document()
        doc.xml_append(doc.xml_create_element(u'entry',
                                       attributes={'id': unicode(param)}))
        doc.entry.xml_append(unicode(param))
        return doc.entry

class TestJN050418_2(TestJN050418):
    #Second simplification of makeEntry
    def makeEntry(self, param):
        doc = amara.create_document()
        doc.xml_append(doc.xml_create_element(u'entry',
                                       attributes={'id': unicode(param)},
                                       content=unicode(param)))
        return doc.entry

class TestJN050418_3(TestJN050418):
    #Third simplification of makeEntry
    def makeEntry(self, param):
        doc = amara.create_document(u'entry',
                                           attributes={'id': unicode(param)},
                                           content=unicode(param))
        return doc.entry

class TestAlain050601:
    XML = """\
<html><head>
<title>Document</title>
</head>
<body>
<script type="text/javascript">
//<![CDATA[
function matchwo(a,b)
{
if (a < b && a > 0) then
   {
   return 1
   }
}
//]]>
</script>
</body>
</html>
"""
    
    def testCdataOutput1(self):
        doc = amara.parse(self.XML)
        import sys
        from Ft.Xml.Xslt.XmlWriter import CdataSectionXmlWriter
        from Ft.Xml.Xslt.OutputParameters import OutputParameters
        doc = parse(text)
        op = OutputParameters()
        op.cdataSectionElements=[(None, u'script')]
        w = CdataSectionXmlWriter(op, sys.stdout)
        out = doc.xml(writer=w)
        #Way too simple.  Fix this test
        self.assert_(out.find('CDATA'))
        return

    def testCdataOutput2(self):
        doc = amara.parse(self.XML)
        out = doc.xml(cdataSectionElements=[u'script']) 
        #Way too simple.  Fix this test
        self.assert_(out.find('CDATA'))
        return

class TestLM050928(TestBase):
    #Luis Morillas reported make_element bug
    def testCreateElement17(self):
        import amara
        import string
        doc = amara.create_document(u'abc')
        for n, l in enumerate(string.letters):
            newLetter = doc.xml_create_element(
                u'letter',
                attributes={'id': unicode(n+1)},
                content= unicode(l)
                )
            doc.abc.xml_append(newLetter)
            #print 'adding', l , '...'
            #if n == 17: break # with 18 elements works fine :-/
        self.assertEqual(len(doc.abc.letter), len(string.letters))
        return


class TestA051123(TestBase):
    #"ancaster" reported empty document create bug
    def testCreateEmptyDoc(self):
        import amara
        doc = amara.create_document()
        doc.xml_append(doc.xml_create_element(u"foo"))
        self.assertEqual(len(doc.xml_children), 1)
        self.assertEqual(len(doc.xml_xpath(u'/')), 1)
        return


class TestIP060124(unittest.TestCase):
    #Ian Phillips reported mangling with rules
    XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<repository xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns="http://www.tibco.com/xmlns/repo/types/2002">
\t<globalVariables>
\t\t<globalVariable>
\t\t\t<name>ADBScriptFileDir</name>
\t\t\t<value>C:\\tibco\\adapter\\adadb\\5.1\\sql</value>
\t\t\t<deploymentSettable>true</deploymentSettable>
\t\t\t<serviceSettable>false</serviceSettable>
\t\t\t<type>String</type>
\t\t\t<modTime>1131636444541</modTime>
\t\t</globalVariable>
\t\t<globalVariable>
\t\t\t<name>Billing</name>
\t\t\t<value>Geneva</value>
\t\t\t<deploymentSettable>false</deploymentSettable>
\t\t\t<serviceSettable>false</serviceSettable>
\t\t\t<type>String</type>
\t\t\t<modTime>1131636444541</modTime>
\t\t</globalVariable>
\t</globalVariables>
</repository>
    """
    MYPREFIXES = { 'gv' : 'http://www.tibco.com/xmlns/repo/types/2002' }
    def testRuleset1(self):
        my_rules = [
            binderytools.ws_strip_element_rule(),
            #binderytools.omit_element_rule( u'gv:deplymentSettable' ),
            #binderytools.omit_element_rule( u'gv:serviceSettable' ),
            #binderytools.omit_element_rule( u'gv:modTime' ),
            #binderytools.simple_string_element_rule( u'gv:name' ),
            #binderytools.simple_string_element_rule( u'gv:value' ),
            #binderytools.simple_string_element_rule( u'gv:type' )
            ]

        doc = amara.parse(self.XML, rules=my_rules, prefixes=self.MYPREFIXES)
        EXPECTED = '<globalVariable xmlns="http://www.tibco.com/xmlns/repo/types/2002"><name>ADBScriptFileDir</name><value>C:\\tibco\\adapter\\adadb\\5.1\sql</value><deploymentSettable>true</deploymentSettable><serviceSettable>false</serviceSettable><type>String</type><modTime>1131636444541</modTime></globalVariable>'
        e = doc.repository.globalVariables.globalVariable[0]
        actual = e.xml()
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(len(e.xml_children), 6)
        self.assertEqual(len(e.xml_xpath(u'.//gv:value')), 1)
        return

    def testRuleset2(self):
        my_rules = [
            binderytools.ws_strip_element_rule(),
            binderytools.omit_element_rule( u'gv:deploymentSettable' ),
            ]

        doc = amara.parse(self.XML, rules=my_rules, prefixes=self.MYPREFIXES)
        EXPECTED = '<globalVariable xmlns="http://www.tibco.com/xmlns/repo/types/2002"><name>ADBScriptFileDir</name><value>C:\\tibco\\adapter\\adadb\\5.1\sql</value><serviceSettable>false</serviceSettable><type>String</type><modTime>1131636444541</modTime></globalVariable>'
        e = doc.repository.globalVariables.globalVariable[0]
        actual = e.xml()
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(len(e.xml_children), 5)
        self.assertEqual(len(e.xml_xpath(u'.//gv:name')), 1)
        self.assertEqual(len(e.xml_xpath(u'.//gv:value')), 1)
        return

    def testRuleset3(self):
        my_rules = [
            binderytools.ws_strip_element_rule(),
            binderytools.omit_element_rule( u'gv:deploymentSettable' ),
            binderytools.simple_string_element_rule( u'gv:name' ),
            ]

        doc = amara.parse(self.XML, rules=my_rules, prefixes=self.MYPREFIXES)
        EXPECTED = '<globalVariable xmlns="http://www.tibco.com/xmlns/repo/types/2002" name="ADBScriptFileDir"><value>C:\\tibco\\adapter\\adadb\\5.1\sql</value><serviceSettable>false</serviceSettable><type>String</type><modTime>1131636444541</modTime></globalVariable>'
        e = doc.repository.globalVariables.globalVariable[0]
        actual = e.xml()
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(len(e.xml_children), 4)
        self.assertEqual(len(e.xml_xpath(u'.//gv:name')), 0)
        self.assertEqual(len(e.xml_xpath(u'.//gv:value')), 1)
        return

    def testRuleset4(self):
        my_rules = [
            binderytools.ws_strip_element_rule(),
            binderytools.omit_element_rule( u'gv:deploymentSettable' ),
            binderytools.omit_element_rule( u'gv:serviceSettable' ),
            binderytools.omit_element_rule( u'gv:modTime' ),
            binderytools.simple_string_element_rule( u'gv:name' ),
            binderytools.simple_string_element_rule( u'gv:value' ),
            binderytools.simple_string_element_rule( u'gv:type' )
            ]

        doc = amara.parse(self.XML, rules=my_rules, prefixes=self.MYPREFIXES)
        EXPECTED = '<globalVariable xmlns="http://www.tibco.com/xmlns/repo/types/2002" type="String" name="ADBScriptFileDir" value="C:\\tibco\\adapter\\adadb\\5.1\\sql"/>'
        e = doc.repository.globalVariables.globalVariable[0]
        actual = e.xml()
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(len(e.xml_children), 0)
        self.assertEqual(len(e.xml_xpath(u'.//gv:name')), 0)
        self.assertEqual(len(e.xml_xpath(u'.//gv:value')), 0)
        return


class TestKS060616(TestBase):
    #Kai Schmitte reported xml_clear() bug
    def testCreateEmptyDoc(self):
        import amara
        xml = '<root><Child1><child2><entry user = "everyone"/><entry user = "site1"/></child2></Child1></root>'
        doc = amara.parse(xml)
        doc.root.Child1.child2.xml_clear()
        EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<root><Child1><child2/></Child1></root>'
        self.assertEqual(len(doc.root.Child1.child2.xml_children), 0)
        self.assertEqual(doc.xml(), EXPECTED)
        return


if __name__ == '__main__':
    unittest.main()

