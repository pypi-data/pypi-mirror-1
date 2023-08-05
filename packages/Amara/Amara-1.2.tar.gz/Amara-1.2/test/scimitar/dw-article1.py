#Basic tests from stron 1.5 spec ( http://xml.ascc.net/resource/schematron/Schematron2000.html )
import sys
import unittest
from util import run_stron

ENCODING = 'utf-8'


STRON1 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Example of let</title>
  <pattern name="Nor too many nor too few dollars">
    <rule context="money">
      <!-- Remove dollar signs and US convention comma separators -->
      <let name="amount" value="number(translate(@amount, '$,', ''))"/>
      <assert test="$amount >= 10000 and $amount &lt;= 1000000">
        Amount should range from ten thousand to  one million dollars
      </assert>
    </rule>
  </pattern>
</schema>
'''

INSTANCE1 = u'<money amount="$300,000.00"/>'.encode(ENCODING)

INSTANCE2 = u'<money amount="500,000"/>'.encode(ENCODING)

INSTANCE3 = u'<money amount="10000.00"/>'.encode(ENCODING)

INSTANCE4 = u'<money amount="$1,000.00"/>'.encode(ENCODING)

INSTANCE5 = u'<money amount="$3,000,000.00"/>'.encode(ENCODING)


STRON2 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Table abstract patterns</title>
  <pattern abstract="true" id="table">
    <rule context="$table">
      <assert test="$row">A table has at least one row</assert>
    </rule>
    <rule context="$row">
      <assert test="$cell">A table row has at least one cell</assert>
    </rule>
  </pattern>

  <pattern name="xhtml-basic-table" is-a="table">
    <param formal="table" actual="table" />
    <param formal="row"  actual="tr" />
    <param formal="cell"  actual="td" />
  </pattern>

  <pattern name="cals-table" is-a="table">
    <param formal="table" actual="ctable" />
    <param formal="row"  actual="tbody/row" />
    <param formal="cell"  actual="entry" />
  </pattern>

  <pattern name="cals-table-extra">
    <rule context="ctable">
      <assert test="tbody">A table has a tbody</assert>
    </rule>
  </pattern>

</schema>
'''

STRON3 = STRON2

STRON_INVALID = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Table abstract patterns</title>
  <pattern abstract="true" id="table">
    <rule context="$table">
      <assert test="$row">A table has at least one row</assert>
    </rule>
    <rule context="$row">
      <assert test="$cell">A table row has at least one cell</assert>
    </rule>
  </pattern>

  <pattern name="xhtml-basic-table" is-a="table">
    <param formal="table" actual="table" />
    <param formal="row"  actual="tr" />
    <param formal="cell"  actual="td" />
  </pattern>

  <pattern name="cals-table" is-a="table">
    <param formal="table" actual="ctable" />
    <param formal="row"  actual="tbody/row" />
    <param formal="cell"  actual="entry" />
    <!-- re:
( (attribute abstract { "true" }, title?, (p*, let*, rule*))
| (attribute abstract { "false" }?, title?, (p*, let*, rule*))
| (attribute abstract { "false" }?, attribute is-a { xsd:IDREF }, title?, (p*,
param*)
)
    -->
    <rule context="ctable">
      <assert test="tbody">A table has a tbody</assert>
    </rule>
  </pattern>

</schema>
'''

STRON4 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Table abstract patterns</title>
  <pattern abstract="true" id="table">
    <rule context="$table">
      <assert test="$row">A table has at least one row</assert>
    </rule>
    <rule context="$row">
      <assert test="$cell">A table row has at least one cell</assert>
    </rule>
    <rule context="$cell">
      <assert test="ancestor::$row">
        Cells can only appear in rows, not '<name path="parent::*"/>'
      </assert>
    </rule>     
  </pattern>

  <pattern name="xhtml-basic-table" is-a="table">
    <param formal="table" actual="table" />
    <param formal="row"  actual="tr" />
    <param formal="cell"  actual="td" />
  </pattern>

  <pattern name="cals-table" is-a="table">
    <param formal="table" actual="ctable" />
    <param formal="row"  actual="tbody/row" />
    <param formal="cell"  actual="entry" />
  </pattern>

  <pattern name="cals-table-extra">
    <rule context="ctable">
      <assert test="tbody">A table has a tbody</assert>
    </rule>
  </pattern>

</schema>
'''

INSTANCE10 = u'''\
<table>
  <tr>
    <td>hello world</td>
  </tr>
</table>
'''.encode(ENCODING)

INSTANCE11 = u'''\
<ctable>
  <tbody>
    <row>
      <entry>hello world</entry>
    </row>
  </tbody>
</ctable>
'''.encode(ENCODING)

INSTANCE12 = u'''\
<table>
  <tr>
  </tr>
</table>
'''.encode(ENCODING)

INSTANCE13 = u'''\
<ctable>
  <tbody>
    <row>
    </row>
  </tbody>
</ctable>
'''.encode(ENCODING)

INSTANCE14 = u'''\
<table>
  <td>
    <tr>
    </tr>
  </td>
</table>
'''.encode(ENCODING)

INSTANCE15 = u'''\
<ctable>
  <tbody>
    <entry>
      <row>
      </row>
    </entry>
  </tbody>
</ctable>
'''.encode(ENCODING)

INSTANCE16 = u'''\
<ctable>
    <row>
      <entry>hello world</entry>
    </row>
</ctable>
'''.encode(ENCODING)

#INSTANCE1 = u'<money amount="$300,000.00"/>'.encode(ENCODING)


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
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example of let\nProcessing pattern: Nor too many nor too few dollars\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test1_2(self):
        output = run_stron(STRON1, INSTANCE2)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        #print output

        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example of let\nProcessing pattern: Nor too many nor too few dollars\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test1_3(self):
        output = run_stron(STRON1, INSTANCE3)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example of let\nProcessing pattern: Nor too many nor too few dollars\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test1_4(self):
        output = run_stron(STRON1, INSTANCE4)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example of let\nProcessing pattern: Nor too many nor too few dollars\nAssertion failure:\nAmount should range from ten thousand to one million dollars\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test1_5(self):
        output = run_stron(STRON1, INSTANCE5)
        #print output
        #normalize text, a bit slow for large files with much non-ws
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Example of let\nProcessing pattern: Nor too many nor too few dollars\nAssertion failure:\nAmount should range from ten thousand to one million dollars\n'
        self.assertEqual(output, expected)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def test2_10(self):
        output = run_stron(STRON2, INSTANCE10)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_11(self):
        output = run_stron(STRON2, INSTANCE11)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_12(self):
        output = run_stron(STRON2, INSTANCE12)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_13(self):
        output = run_stron(STRON2, INSTANCE13)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_14(self):
        output = run_stron(STRON2, INSTANCE14)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nAssertion failure:\nA table has at least one row\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_15(self):
        output = run_stron(STRON2, INSTANCE15)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table has at least one row\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test2_16(self):
        output = run_stron(STRON2, INSTANCE16)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table has at least one row\nProcessing pattern: cals-table-extra\nAssertion failure:\nA table has a tbody\n'
        self.assertEqual(output, expected)
        return

    def test3_10(self):
        output = run_stron(STRON3, INSTANCE10)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_11(self):
        output = run_stron(STRON3, INSTANCE11)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_12(self):
        output = run_stron(STRON3, INSTANCE12)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_13(self):
        output = run_stron(STRON3, INSTANCE13)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_14(self):
        output = run_stron(STRON3, INSTANCE14)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nAssertion failure:\nA table has at least one row\nAssertion failure:\nA table row has at least one cell\nProcessing pattern: cals-table\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_15(self):
        output = run_stron(STRON3, INSTANCE15)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table has at least one row\nProcessing pattern: cals-table-extra\n'
        self.assertEqual(output, expected)
        return

    def test3_16(self):
        output = run_stron(STRON3, INSTANCE16)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Table abstract patterns\nProcessing pattern: xhtml-basic-table\nProcessing pattern: cals-table\nAssertion failure:\nA table has at least one row\nProcessing pattern: cals-table-extra\nAssertion failure:\nA table has a tbody\n'
        self.assertEqual(output, expected)
        return


if __name__ == '__main__':
    unittest.main()

