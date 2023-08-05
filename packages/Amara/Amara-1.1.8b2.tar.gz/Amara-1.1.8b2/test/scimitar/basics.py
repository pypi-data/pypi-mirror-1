#Basic tests from stron 1.5 spec ( http://xml.ascc.net/resource/schematron/Schematron2000.html )
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


INSTANCE1 = u'<dog><ear/><ear/></dog>'.encode(ENCODING)

INSTANCE2 = u'''\
<dog><ear/></dog>'''.encode(ENCODING)

INSTANCE3 = u'''\
<dog><ear/><bone/><ear/></dog>'''.encode(ENCODING)

INSTANCE4 = u'''\
<dog><ear/><bone/></dog>'''.encode(ENCODING)


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


if __name__ == '__main__':
    unittest.main()

