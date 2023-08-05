#Test examples in http://uche.ogbuji.net/tech/pubs/schematron.html
import sys
import unittest
from util import run_stron


ENCODING = 'utf-8'


#Listing 5 with root context hack in place
#Includes bug fix to article listing: removed erroneous addr: prefix in first assert
LISTING5_1 = '''\
<schema xmlns='http://purl.oclc.org/dsdl/schematron'>
        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="ENTRY">
                        <assert test="count(NAME) = 1">Validation error: <name/> element missing a NAME child.</assert>
                        <assert test="count(ADDRESS) = 1">Validation error: <name/> element missing an ADDRESS child.</assert>
                        <assert test="count(EMAIL) = 1">Validation error: <name/> element missing an EMAIL child.</assert>
                        <assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence</assert>
                        <assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY</assert>
                </rule>
                <rule context="PHONENUM">
                        <assert test="@DESC">Validation error: <name/> must have a DESC attribute</assert>
                </rule>
        </pattern>
</schema>'''

#Listing 5 without root context hack
#Includes bug fix to article listing: removed erroneous addr: prefix in first assert
LISTING5_2 = '''\
<schema xmlns='http://purl.oclc.org/dsdl/schematron'>
        <pattern name="Structural Validation">
                <rule context="/">
                        <assert test="ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="ENTRY">
                        <assert test="count(NAME) = 1">Validation error: <name/> element missing a NAME child.</assert>
                        <assert test="count(ADDRESS) = 1">Validation error: <name/> element missing an ADDRESS child.</assert>
                        <assert test="count(EMAIL) = 1">Validation error: <name/> element missing an EMAIL child.</assert>
                        <assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence</assert>
                        <assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY</assert>
                </rule>
                <rule context="PHONENUM">
                        <assert test="@DESC">Validation error: <name/> must have a DESC attribute</assert>
                </rule>
        </pattern>
</schema>'''

#Listing 6 with root context hack in place
LISTING6_1 = '''\
<schema xmlns='http://purl.oclc.org/dsdl/schematron'>

        <ns prefix='addr' uri='http://addressbookns.com'/>

        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="addr:ENTRY">
                        <assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of <name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        </assert>
                        <assert test="count(addr:NAME) = 1">
Validation error: <name/> element missing a NAME child.
                        </assert>
                        <assert test="count(addr:ADDRESS) = 1">
Validation error: <name/> element missing an ADDRESS child.
                        </assert>
                        <assert test="count(addr:EMAIL) = 1">
Validation error: <name/> element missing an EMAIL child.
                        </assert>
                        <assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        </assert>
                        <assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        </assert>
                </rule>
                <rule context="addr:PHONENUM">
                        <assert test="@DESC">
Validation error: <name/> must have a DESC attribute
                        </assert>
                </rule>
        </pattern>
        <pattern name="Government Contact Report">
                <rule context="addr:EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        </report>
                </rule>
        </pattern>
</schema>'''

#Listing 6 without root context hack
LISTING6_2 = '''\
<schema xmlns='http://purl.oclc.org/dsdl/schematron'>

        <ns prefix='addr' uri='http://addressbookns.com'/>

        <pattern name="Structural Validation">
                <rule context="/">
                        <assert test="addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="addr:ENTRY">
                        <assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of <name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        </assert>
                        <assert test="count(addr:NAME) = 1">
Validation error: <name/> element missing a NAME child.
                        </assert>
                        <assert test="count(addr:ADDRESS) = 1">
Validation error: <name/> element missing an ADDRESS child.
                        </assert>
                        <assert test="count(addr:EMAIL) = 1">
Validation error: <name/> element missing an EMAIL child.
                        </assert>
                        <assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        </assert>
                        <assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        </assert>
                </rule>
                <rule context="addr:PHONENUM">
                        <assert test="@DESC">
Validation error: <name/> must have a DESC attribute
                        </assert>
                </rule>
        </pattern>
        <pattern name="Government Contact Report">
                <rule context="addr:EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        </report>
                </rule>
        </pattern>
</schema>'''

LISTING2 = u'''\
<?xml version = "1.0"?>
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>'''.encode(ENCODING)

LISTING4 = u'''\
<?xml version = "1.0"?>
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <SPAM>Make money fast</SPAM>
        </ENTRY>
        <EXTRA/>
</ADDRBOOK>
'''.encode(ENCODING)

LISTING7 = u'''\
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME xmlns='http://bogus.com'>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME xmlns='http://bogus.com'>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>
'''.encode(ENCODING)

LISTING8 = u'''\
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Manfredo Manfredi</NAME>
                <ADDRESS>4414 Palazzo Terrace</ADDRESS>
                <PHONENUM DESC="Work">888-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">888-555-7677</PHONENUM>
                <EMAIL>mpm@scudetto.dom.gov</EMAIL>
        </ENTRY>
</ADDRBOOK>'''.encode(ENCODING)


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestBasics(unittest.TestCase):
    def setUp(self):
        #self.isrc_factory = InputSource.DefaultFactory
        return

    def testStron1_1(self):
        output = run_stron(LISTING5_1, LISTING2)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\n'
        self.assertEqual(output, expected)
        return

    def testStron1_2(self):
        output = run_stron(LISTING5_2, LISTING2)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\n'
        self.assertEqual(output, expected)
        return

    def testStron1_3(self):
        output = run_stron(LISTING5_1, LISTING4)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nAssertion failure:\nValidation error: ENTRY element missing an ADDRESS child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\n'
        self.assertEqual(output, expected)
        return

    def testStron1_4(self):
        output = run_stron(LISTING5_2, LISTING4)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nAssertion failure:\nValidation error: ENTRY element missing an ADDRESS child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\n'
        self.assertEqual(output, expected)
        return

    def testStron2_1(self):
        output = run_stron(LISTING6_1, LISTING7)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nAssertion failure:\nValidation error: all children of ENTRY must either be in the namespace \'http://addressbookns.com\' or in a namespace containing the substring \'extension\'.\nAssertion failure:\nValidation error: ENTRY element missing a NAME child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\nAssertion failure:\nValidation error: all children of ENTRY must either be in the namespace \'http://addressbookns.com\' or in a namespace containing the substring \'extension\'.\nAssertion failure:\nValidation error: ENTRY element missing a NAME child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\nProcessing pattern: Government Contact Report\n'
        self.assertEqual(output, expected)
        return

    def testStron2_2(self):
        output = run_stron(LISTING6_2, LISTING7)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nAssertion failure:\nValidation error: all children of ENTRY must either be in the namespace \'http://addressbookns.com\' or in a namespace containing the substring \'extension\'.\nAssertion failure:\nValidation error: ENTRY element missing a NAME child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\nAssertion failure:\nValidation error: all children of ENTRY must either be in the namespace \'http://addressbookns.com\' or in a namespace containing the substring \'extension\'.\nAssertion failure:\nValidation error: ENTRY element missing a NAME child.\nAssertion failure:\nValidation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence\nAssertion failure:\nValidation error: there is an extraneous element child of ENTRY\nProcessing pattern: Government Contact Report\n'
        self.assertEqual(output, expected)
        return

    def testStron2_3(self):
        output = run_stron(LISTING6_1, LISTING8)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nProcessing pattern: Government Contact Report\nReport:\nThis address book contains government contacts.\n'
        self.assertEqual(output, expected)
        return

    def testStron2_4(self):
        output = run_stron(LISTING6_2, LISTING8)
        output = normalize_text(output)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Processing pattern: Structural Validation\nProcessing pattern: Government Contact Report\nReport:\nThis address book contains government contacts.\n'
        self.assertEqual(output, expected)
        return


if __name__ == '__main__':
    unittest.main()

