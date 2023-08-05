#Test examples in http://uche.ogbuji.net/tech/pubs/schematron.html
import sys
import unittest
from util import run_stron

ABS_RULE_STRON = '''\
<sch:schema xmlns:sch="http://www.ascc.net/xml/schematron" >
     <sch:title>Abstract rules</sch:title>
     <sch:pattern name="Check items" see="http://zvon.org/friendsRule.html">
          <sch:rule context="email">
               <sch:extends rule="phone"/>
               <sch:extends rule="email"/>
          </sch:rule>
          <sch:rule abstract="yes" id="phone">
               <sch:assert test="../phone">There is no phone.</sch:assert>
          </sch:rule>
          <sch:rule abstract="yes" id="email">
               <sch:assert test="contains(.,'@')"> @ is missing</sch:assert>
               <sch:report test="contains(normalize-space(.),' ')">Whitespace inside address</sch:report>
          </sch:rule>
     </sch:pattern>
</sch:schema>'''

ABS_RULE_CANDIDATE = '''\
<friends>
     <friend>
          <name>John Smith</name>
          <email>John.Smith#yahoo.com</email>
          <phone>123452</phone>
     </friend>
     <friend>
          <name>Jane Brown</name>
          <email>Jane Brown@home.org</email>
     </friend>
</friends> '''


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestZvon(unittest.TestCase):
    def testAbsRule(self):
        output = run_stron(ABS_RULE_STRON, ABS_RULE_CANDIDATE, True)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Abstract rules\nProcessing pattern: Check items\nAssertion failure:\n@ is missing\nAssertion failure:\nThere is no phone.\nReport:\nWhitespace inside address\n'
        self.assertEqual(output, expected)
        return


if __name__ == '__main__':
    unittest.main()

