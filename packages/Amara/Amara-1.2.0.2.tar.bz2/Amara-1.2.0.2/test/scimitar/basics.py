import sys
import unittest
from util import run_stron


ENCODING = 'utf-8'


STRON1 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO">
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="count(ear) = 2"
    >A 'dog' element should contain two 'ear' elements.</sch:assert>
    <sch:report test="bone"
    >This dog has a bone.</sch:report>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON2 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO">
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="count(ear) = 2"
    >A '<sch:name/>' element should contain two 'ear' elements. Test value: <sch:value-of select="10*10"/></sch:assert>
    <sch:report test="bone"
    >This dog has a bone.</sch:report>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON3 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO">
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
  <sch:rule context="dog" >
   <sch:assert test="nose | @exceptional='true'" diagnostics="d1 d2"
   >A dog should have a nose.</sch:assert>
  </sch:rule>
 </sch:pattern>

 <sch:diagnostics>
 <sch:diagnostic id="d1"
 >Your dog <sch:value-of select="@petname" /> has no nose. 
 How does he smell? Terrible. Give him a nose element,
 putting it after the <sch:name path="child::*[2]"/> element.
 </sch:diagnostic>
 <sch:diagnostic id="d2"
 >Animals such as <sch:name/> usually come with a full complement
 of legs, ears and noses, etc. However, exceptions are possible.
 If your dog is exceptional, provide an attribute
 <sch:emph>exceptional='true'</sch:emph>
 </sch:diagnostic>
</sch:diagnostics>
</sch:schema>
'''

STRON4 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO">
 <sch:title>Example with problem patterns</sch:title>
 <sch:pattern>
 </sch:pattern>
 <sch:pattern>
   <sch:rule>
    <sch:assert test="count(ear) = 2"
    >A 'dog' element should contain two 'ear' elements.</sch:assert>
   </sch:rule>
 </sch:pattern>
</sch:schema>
'''

STRON5 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO" %s>
 <sch:title>Example Schematron Schema</sch:title>
 <sch:phase id='PH1'>
  <sch:active pattern='PAT1'/>
 </sch:phase>
 <sch:phase id='PH2'>
  <sch:active pattern='PAT2'/>
 </sch:phase>
 <sch:phase id='PH3'>
  <sch:active pattern='PAT1'/>
  <sch:active pattern='PAT2'/>
 </sch:phase>
 <!-- The two rules int he two patterns are redundant.  This is just for testing -->
 <sch:pattern id='PAT1'>
   <sch:rule context="dog">
    <sch:assert test="count(ear) = 2"
    >A 'dog' element should contain two 'ear' elements.</sch:assert>
   </sch:rule>
  </sch:pattern>
  <sch:pattern id='PAT2'>
   <sch:rule context="dog">
    <sch:assert test="name(*[2]) = 'ear'"
    >The second child of a '<sch:name/>' element should be an 'ear' element.</sch:assert>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON6 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO" %s>
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="generate-id(ear) != ''">Should never fire.</sch:assert>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON7 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"
            version="ISO" %s>
 <sch:title>Example Schematron Schema</sch:title>
 <sch:ns uri="http://exslt.org/regular-expressions" prefix="regex"/>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="regex:test(name(*), '.*s')">The first child element's name should end with 's'.</sch:assert>
    <sch:assert test="count(regex:match(name(*), 'e')) = 1">The first child element's name should contain one 'e'.</sch:assert>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON8 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" version="ISO" %s>
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="a">
    <sch:assert test="count(b[normalize-space() = current()/b[position() = 1]]) != 2">Should never fire.</sch:assert>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON_EVDV_060812 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="exslt">
    <ns prefix="regexp" uri="http://exslt.org/regular-expressions"/>
    <pattern>
        <rule context="*">
          <let name="matches" value="regexp:match(normalize-space(.), '\.')"/>
          <report test="$matches">Found a dot in <name/></report>
        </rule>
    </pattern>
</schema>
'''

STRON_EVDV_060914 = '''\
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="exslt">
  <ns prefix="regexp" uri="http://exslt.org/regular-expressions"/>
  <pattern fpi="test-doc">
    <rule context="/">
      <assert test="document('dummy.xml')">Unable to load document</assert>
    </rule>
  </pattern>
</schema>
'''

STRONX = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"
            xmlns:regex="http://exslt.org/regular-expressions"
            version="ISO" %s>
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="regex:match(name(*), 'e.*')">The first child element's name should start with 'e'.</sch:assert>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''

OBSOLETE_STRON = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://www.ascc.net/xml/schematron" version="ISO">
 <sch:title>Example Schematron Schema</sch:title>
 <sch:pattern>
   <sch:rule context="dog">
    <sch:assert test="count(ear) = 2"
    >A 'dog' element should contain two 'ear' elements.</sch:assert>
    <sch:report test="bone"
    >This dog has a bone.</sch:report>
   </sch:rule>
  </sch:pattern>
</sch:schema>
'''


INSTANCE1 = u'<dog><ear/><ear/></dog>'.encode(ENCODING)

INSTANCE2 = u'''\
<dog><ear/></dog>'''.encode(ENCODING)

INSTANCE3 = u'''\
<dog><ear/><bone/><ear/></dog>'''.encode(ENCODING)

INSTANCE4 = u'''\
<dog><ear/><bone/></dog>'''.encode(ENCODING)

INSTANCE5 = u'''\
<a><b>.</b><c></c><d> . </d></a>'''.encode(ENCODING)


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestBasics(unittest.TestCase):
    def testStron1(self):
        output = run_stron(STRON1, INSTANCE1)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron2(self):
        output = run_stron(STRON1, INSTANCE3)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nReport:\nThis dog has a bone.\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron3(self):
        output = run_stron(STRON1, INSTANCE2)
        output = normalize_text(output)

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron4(self):
        output = run_stron(STRON3, INSTANCE1)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA dog should have a nose.\nDiagnostic message:\nYour dog has no nose. How does he smell? Terrible. Give him a nose element,\nputting it after the ear element.\nDiagnostic message:\nAnimals such as dog usually come with a full complement\nof legs, ears and noses, etc. However, exceptions are possible.\nIf your dog is exceptional, provide an attribute\n<emph>exceptional=\'true\'</emph>\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron5(self):
        output = run_stron(STRON3, INSTANCE2)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA dog should have a nose.\nDiagnostic message:\nYour dog has no nose. How does he smell? Terrible. Give him a nose element,\nputting it after the element.\nDiagnostic message:\nAnimals such as dog usually come with a full complement\nof legs, ears and noses, etc. However, exceptions are possible.\nIf your dog is exceptional, provide an attribute\n<emph>exceptional=\'true\'</emph>\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron6(self):
        output = run_stron(STRON3, INSTANCE3)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA dog should have a nose.\nDiagnostic message:\nYour dog has no nose. How does he smell? Terrible. Give him a nose element,\nputting it after the bone element.\nDiagnostic message:\nAnimals such as dog usually come with a full complement\nof legs, ears and noses, etc. However, exceptions are possible.\nIf your dog is exceptional, provide an attribute\n<emph>exceptional=\'true\'</emph>\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron7(self):
        output = run_stron(STRON1, INSTANCE4)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\nReport:\nThis dog has a bone.\n'
        self.assertEqual(output, expected)
        return

    def testStron8(self):
        self.assertRaises(TypeError,
                          run_stron, STRON4, INSTANCE1)
        return

    def testStron9(self):
        #Default phase
        output = run_stron(STRON5%'', INSTANCE2)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)

    def testStron10(self):
        output = run_stron(STRON5%'', INSTANCE2, phase='#ALL')
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)

    def testStron11(self):
        output = run_stron(STRON5%'', INSTANCE2, phase='#DEFAULT')
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)

    def testStron12(self):
        output = run_stron(STRON5%'', INSTANCE2, phase='PH1')
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\n'
        self.assertEqual(output, expected)

    def testStron13(self):
        output = run_stron(STRON5%'', INSTANCE2, phase='PH2')
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)
        return

    def testStron14(self):
        output = run_stron(STRON5%'', INSTANCE2, phase='PH3')
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nA \'dog\' element should contain two \'ear\' elements.\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)

    def testStron15(self):
        output = run_stron(STRON5%' defaultPhase="PH2"', INSTANCE2)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nThe second child of a \'dog\' element should be an \'ear\' element.\n'
        self.assertEqual(output, expected)

    def testStron16(self):
        output = run_stron(STRON6%' queryBinding="xslt"', INSTANCE1)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\n'
        self.assertEqual(output, expected)

    def testStron17(self):
        from Ft.Xml.XPath import RuntimeException
        self.assertRaises(RuntimeException,
                          run_stron, STRON6%' queryBinding="xpath"', INSTANCE1)

    def testStron18(self):
        output = run_stron(STRON7%' queryBinding="exslt"', INSTANCE1)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\nAssertion failure:\nThe first child element\'s name should end with \'s\'.\n'
        self.assertEqual(output, expected)

    def testStron19(self):
        output = run_stron(STRON8%' queryBinding="exslt"', INSTANCE5)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example Schematron Schema\nProcessing pattern: [unnamed]\n'
        self.assertEqual(output, expected)

    def testStronVdv1(self):
        output = run_stron(STRON_EVDV_060812, INSTANCE5)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: [unnamed]\nReport:\nFound a dot in a\nReport:\nFound a dot in b\nReport:\nFound a dot in d\n'
        self.assertEqual(output, expected)

    def testStronVdv2(self):
        from Ft.Xml import InputSource
        from Ft.Lib import Uri
        isrc_factory = InputSource.DefaultFactory
        stron_isrc = isrc_factory.fromString(STRON_EVDV_060914, Uri.OsPathToUri(''))
        #from Ft.Xml import CreateInputSource
        output = run_stron(stron_isrc, INSTANCE5)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: [unnamed]\n'
        self.assertEqual(output, expected)



class TestOddCases(unittest.TestCase):
    def testObsoleteNamespace(self):
        self.assertRaises(RuntimeError,
                          run_stron, OBSOLETE_STRON, INSTANCE1)
        #import warnings
        #warnings.filterwarnings('error', '.*', DeprecationWarning)
        #self.assertRaises(DeprecationWarning,
        #                  run_stron, OBSOLETE_STRON, INSTANCE1)


if __name__ == '__main__':
    unittest.main()

