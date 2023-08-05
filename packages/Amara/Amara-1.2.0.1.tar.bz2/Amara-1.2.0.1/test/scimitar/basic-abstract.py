import sys
import unittest
from util import run_stron

ENCODING = 'utf-8'


STRON1 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Abstract test</title>
  <pattern abstract="true" id="abs1">
    <rule context="$a">
      <assert test="$b"><name path="$c"/> and <value-of select="$d"/></assert>
    </rule>
  </pattern>

  <pattern name="concrete1" is-a="abs1">
    <param formal="a" actual="actual-a"/>
    <param formal="b"  actual="actual-b"/>
    <param formal="c"  actual="actual-c"/>
    <param formal="d"  actual="actual-d"/>
  </pattern>
</schema>
'''

STRON2 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Abstract test</title>
  <pattern abstract="true" id="abs1">
    <rule context="$a">
      <assert test="$aa"><name path="$aaa"/> and <value-of select="$aaaa"/></assert>
    </rule>
  </pattern>

  <pattern name="concrete1" is-a="abs1">
    <param formal="a" actual="actual-a"/>
    <param formal="aa"  actual="actual-b"/>
    <param formal="aaa"  actual="actual-c"/>
    <param formal="aaaa"  actual="actual-d"/>
  </pattern>
</schema>
'''

INSTANCE1 = u'<actual-a><actual-b/><actual-c/><actual-d>boo</actual-d></actual-a>'.encode(ENCODING)

INSTANCE2 = u'<actual-a><actual-c/><actual-d>boo</actual-d></actual-a>'.encode(ENCODING)


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestBasics(unittest.TestCase):
    def setUp(self):
        #self.isrc_factory = InputSource.DefaultFactory
        return

    def test1_1(self):
        output = run_stron(STRON1, INSTANCE1)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Abstract test\nProcessing pattern: concrete1\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test1_2(self):
        output = run_stron(STRON1, INSTANCE2)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Abstract test\nProcessing pattern: concrete1\nAssertion failure:\nactual-c and boo\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test2_1(self):
        output = run_stron(STRON2, INSTANCE1)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Abstract test\nProcessing pattern: concrete1\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test2_2(self):
        output = run_stron(STRON2, INSTANCE2)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Abstract test\nProcessing pattern: concrete1\nAssertion failure:\nactual-c and boo\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return


if __name__ == '__main__':
    unittest.main()

