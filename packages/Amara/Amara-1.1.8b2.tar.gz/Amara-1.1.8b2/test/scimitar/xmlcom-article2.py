#Test examples in http://www.xml.com/pub/a/2003/11/12/schematron.html
import sys
import unittest
from util import run_stron


ENCODING = 'utf-8'


#Note: fixed a typo in the article: missing parenthesis after 'Male' in assert test
STRON1 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
    <pattern name="Check structure">
        <rule context="Person">
            <assert test="@Title">The element Person must have a Title attribute.</assert>
            <assert test="count(*) = 2 and count(Name) = 1 and count(Gender) = 1">The element Person should have the child elements Name and Gender.</assert>
            <assert test="*[1] = Name">The element Name must appear before element Age.</assert>
            <assert test="(@Title = 'Mr' and Gender = 'Male') or @Title != 'Mr'">If the Title is "Mr" then the gender of the person must be "Male".</assert>
        </rule>
    </pattern>
</schema>
'''

STRON2 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
    <sch:ns uri="http://www.topologi.com/example" prefix="ex"/>
    <sch:pattern name="Check structure">
        <sch:rule context="ex:Person">
            <sch:assert test="@Title">The element Person must have a Title attribute</sch:assert>
            <sch:assert test="count(ex:*) = 2 and count(ex:Name) = 1 and count(ex:Gender) = 1">The element Person should have the child elements Name and Gender.</sch:assert>
            <sch:assert test="ex:*[1] = ex:Name">The element Name must appear before element Gender.</sch:assert>
        </sch:rule>
    </sch:pattern>
    <sch:pattern name="Check co-occurrence constraints">
        <sch:rule context="ex:Person">
            <sch:assert test="(@Title = 'Mr' and ex:Gender = 'Male') or @Title != 'Mr'">If the Title is "Mr" then the gender of the person must be "Male".</sch:assert>
        </sch:rule>
    </sch:pattern>
</sch:schema>
'''

STRON3 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:pattern name="Time" abstract="true">
    <sch:rule context="$time">
        <sch:assert test="$hour>=0 and $hour&lt;=23">The hour must be a value between 0 and 23.</sch:assert>
        <sch:assert test="$minute>=0 and $minute&lt;=59">The minutes must be a value between 0 and 59.</sch:assert>
        <sch:assert test="$second>=0 and $second&lt;=59">The seconds must be a value between 0 and 23.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern name="SingleLineTime" is-a="Time">
    <sch:param formal="time" actual="time"/>
    <sch:param formal="hour" actual="number(substring(.,1,2))"/>
    <sch:param formal="minute" actual="number(substring(.,4,2))"/>
    <sch:param formal="second" actual="number(substring(.,7,2))"/>
  </sch:pattern>
</sch:schema>
'''

STRON4 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:pattern name="Time" abstract="true">
    <sch:rule context="$time">
        <sch:assert test="$hour>=0 and $hour&lt;=23">The hour must be a value between 0 and 23.</sch:assert>
        <sch:assert test="$minute>=0 and $minute&lt;=59">The minutes must be a value between 0 and 59.</sch:assert>
        <sch:assert test="$second>=0 and $second&lt;=59">The seconds must be a value between 0 and 23.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern name="MultiLineTime" is-a="Time">
    <sch:param formal="time" actual="time"/>
    <sch:param formal="hour" actual="hour"/>
    <sch:param formal="minute" actual="minute"/>
    <sch:param formal="second" actual="second"/>
  </sch:pattern>
</sch:schema>
'''

STRON5 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:pattern name="Time" abstract="true">
    <sch:rule context="$time">
        <sch:assert test="$hour>=0 and $hour&lt;=23">The hour must be a value between 0 and 23.</sch:assert>
        <sch:assert test="$minute>=0 and $minute&lt;=59">The minutes must be a value between 0 and 59.</sch:assert>
        <sch:assert test="$second>=0 and $second&lt;=59">The seconds must be a value between 0 and 23.</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern name="Dummy pattern">
    <sch:rule context="dummy">
      <sch:assert test="false()">Should not be invoked</sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern name="MultiLineTime" is-a="Time">
    <sch:param formal="time" actual="time"/>
    <sch:param formal="hour" actual="hour"/>
    <sch:param formal="minute" actual="minute"/>
    <sch:param formal="second" actual="second"/>
  </sch:pattern>

  <sch:pattern name="Dummy pattern">
    <sch:rule context="dummy">
      <sch:assert test="false()">Should not be invoked</sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
'''

STRON6 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:pattern name="Time">
    <sch:rule context="time">
      <sch:let name="hour" value="number(substring(.,1,2))"/>
      <sch:let name="minute" value="number(substring(.,4,2))"/>
      <sch:let name="second" value="number(substring(.,7,2))"/>

      <!-- CHECK FOR VALID HH:MM:SS -->
      <sch:assert test="string-length(.)=8 and substring(.,3,1)=':' and substring(.,6,1)=':'">The time element should contain a time in the format HH:MM:SS.</sch:assert>
      <sch:assert test="$hour>=0 and $hour&lt;=23">The hour must be a value between 0 and 23.</sch:assert>
      <sch:assert test="$minute>=0 and $minute&lt;=59">The minutes must be a value between 0 and 59.</sch:assert>
      <sch:assert test="$second>=0 and $second&lt;=59">The second must be a value between 0 and 59.</sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
'''


INSTANCE1 = u'''<Person Title="Mr">
    <Name>Eddie</Name>
    <Gender>Male</Gender>
</Person>'''.encode(ENCODING)

INSTANCE2 = u'''\
<ex:Person Title="Mr" xmlns:ex="http://www.topologi.com/example">
    <ex:Name>Eddie</ex:Name>
    <ex:Gender>Male</ex:Gender>
</ex:Person>'''.encode(ENCODING)

INSTANCE3 = u'''\
<dog><ear/><bone/><ear/></dog>'''.encode(ENCODING)

INSTANCE4 = u'''\
<dog><ear/><bone/></dog>'''.encode(ENCODING)

INSTANCE5 = u'''\
<time>21:45:12</time>'''.encode(ENCODING)

INSTANCE6 = u'''\
<time>
    <hour>21</hour>
    <minute>45</minute>
    <second>12</second>
</time>'''.encode(ENCODING)


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestBasics(unittest.TestCase):
    def setUp(self):
        #self.isrc_factory = InputSource.DefaultFactory
        return

    def testStron1_1(self):
        output = run_stron(STRON1, INSTANCE1)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Check structure\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron2_2(self):
        output = run_stron(STRON2, INSTANCE2)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Check structure\nProcessing pattern: Check co-occurrence constraints\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron3_5(self):
        output = run_stron(STRON3, INSTANCE5)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: SingleLineTime\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron3_6(self):
        output = run_stron(STRON3, INSTANCE6)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: SingleLineTime\nAssertion failure:\nThe hour must be a value between 0 and 23.\nAssertion failure:\nThe minutes must be a value between 0 and 59.\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron4_5(self):
        output = run_stron(STRON4, INSTANCE5)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: MultiLineTime\nAssertion failure:\nThe hour must be a value between 0 and 23.\nAssertion failure:\nThe minutes must be a value between 0 and 59.\nAssertion failure:\nThe seconds must be a value between 0 and 23.\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron4_6(self):
        output = run_stron(STRON4, INSTANCE6)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: MultiLineTime\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron5_5(self):
        output = run_stron(STRON5, INSTANCE5)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Dummy pattern\nProcessing pattern: MultiLineTime\nAssertion failure:\nThe hour must be a value between 0 and 23.\nAssertion failure:\nThe minutes must be a value between 0 and 59.\nAssertion failure:\nThe seconds must be a value between 0 and 23.\nProcessing pattern: Dummy pattern\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron5_6(self):
        output = run_stron(STRON5, INSTANCE6)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Dummy pattern\nProcessing pattern: MultiLineTime\nProcessing pattern: Dummy pattern\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron6_5(self):
        output = run_stron(STRON6, INSTANCE5)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Time\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testStron6_6(self):
        output = run_stron(STRON6, INSTANCE6)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Time\nAssertion failure:\nThe time element should contain a time in the format HH:MM:SS.\nAssertion failure:\nThe hour must be a value between 0 and 23.\nAssertion failure:\nThe minutes must be a value between 0 and 59.\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return


if __name__ == '__main__':
    unittest.main()

