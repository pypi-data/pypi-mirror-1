#Test examples in ...
import sys
import cStringIO
import unittest
from util import run_stron

ENCODING = 'utf-8'


STRON1 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Special XHTML conventions</title>
  <ns uri="http://www.w3.org/1999/xhtml" prefix="html"/>
  <pattern name="Document head">
    <rule context="html:head">
      <assert test="html:title">Page does not have a title.</assert>
      <assert test="html:link/@rel = 'stylesheet'
                    and html:link/@type = 'text/css'
                    and html:link/@href = 'std.css'">
        Page does not use the standard stylesheet.
      </assert>
      <report test="html:style">
        Page uses in-line style rather than linking to the
        standard stylesheet.
      </report>
    </rule>
  </pattern>
  <pattern name="Document body">
    <rule context="html:body">
      <assert test="@class = 'std-body'">
        Page does not use the standard body class.
      </assert>
      <assert test="html:*[1]/self::html:div[@class = 'std-top']">
        Page does not start with the required page top component
      </assert>
    </rule>
  </pattern>
</schema>
'''

DTDECL = u'''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
'''

INSTANCE1 = u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" type="text/css" href="std.css"/>
    <title>Document head</title>
  </head>
  <body class="std-body">
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING)


INSTANCE2 = u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Document head</title>
    <style>
      body.std-body { background white; }
    </style>
  </head>
  <body class="std-body">
    <h1>Title</h1>
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING)


INSTANCE3 = u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" type="text/css" href="std.css"/>
  </head>
  <body>
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING)

EXAMPLES = []

EG_3_1 = (
'eg3_1',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Document root">
    <rule context="/">
      <assert test="doc">Root element should be "doc".</assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'<doc/>'.encode(ENCODING), '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\n'),
),
(
(u'<bogus/>'.encode(ENCODING), '<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nAssertion failure:\nRoot element should be "doc".\n'),
)
)

EXAMPLES += [EG_3_1]

EG_3_2 = (
'eg3_2',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Major elements">
    <rule context="doc">
      <assert test="prologue">
        The "doc" element must have a "prologue" child.
      </assert>
      <assert test="section">
        The "doc" element must have at least one "section" child.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\n'),
(u'''\
<doc>
  <prologue/>
  <section/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\n')
),
(
(u'''\
<doc>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\nThe "doc" element must have a "prologue" child.\n'),
(u'''\
<doc>
  <prologue/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\nThe "doc" element must have at least one "section" child.\n'),
(u'''\
<doc/>
'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\nThe "doc" element must have a "prologue" child.\nAssertion failure:\nThe "doc" element must have at least one "section" child.\n')
)
)

EXAMPLES += [EG_3_2]

EG_3_3 = (
'eg3_3',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Extaneous docs">
    <rule context="doc">
      <assert test="not(ancestor::*)">
        The "doc" element is only allowed at the document root.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'<doc><ok/></doc>'.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Extaneous docs\n'),
),
(
(u'<doc><doc/></doc>'.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Extaneous docs\nAssertion failure:\nThe "doc" element is only allowed at the document root.\n'),
)
)

EXAMPLES += [EG_3_3]

EG_3_4 = (
'eg3_4',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Extraneous docs">
    <rule context="prologue">
      <assert test="not(preceding-sibling::section)">
        No "section" may occur before the "prologue".
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue/>
  <section/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Extraneous docs\n'),
),
(
(u'''\
<doc>
  <section/>
  <prologue/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Extraneous docs\nAssertion failure:\nNo "section" may occur before the "prologue".\n'),
)
)

EXAMPLES += [EG_3_4]

EG_3_5 = (
'eg3_5',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Title with subtitle">
    <rule context="title">
      <assert test="following-sibling::*[1]/self::subtitle">
        A "title" must be immediately followed by a "subtitle".
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\nAssertion failure:\nA "title" must be immediately followed by a "subtitle".\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <midtitle>Seriously</midtitle>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\nAssertion failure:\nA "title" must be immediately followed by a "subtitle".\n'),
)
)

EXAMPLES += [EG_3_5]

EG_3_6 = (
'eg3_6',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Minimum keywords">
    <rule context="prologue">
      <assert test="count(keyword) > 2">
        At least three keywords are required.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <keyword>tachyon</keyword>
    <keyword>higgs</keyword>
    <keyword>propulsion</keyword>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Minimum keywords\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <keyword>tachyon</keyword>
    <keyword>higgs</keyword>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Minimum keywords\nAssertion failure:\nAt least three keywords are required.\n'),
)
)

EXAMPLES += [EG_3_6]

EG_3_7 = (
'eg3_7',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Author attributes">
    <rule context="author">
      <assert test="@e-mail">
        author must have e-mail attribute.
      </assert>
      <assert test="@member = 'yes' or @member = 'no'">
        author must have member attribute with 'yes' or 'no' value.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author attributes\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes'>Chikezie Emereuwa</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author attributes\nAssertion failure:\nauthor must have e-mail attribute.\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author attributes\nAssertion failure:\nauthor must have member attribute with \'yes\' or \'no\' value.\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='maybe' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author attributes\nAssertion failure:\nauthor must have member attribute with \'yes\' or \'no\' value.\n'),
)
)

EXAMPLES += [EG_3_7]

EG_3_8 = (
'eg3_8',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Useful title">
    <rule context="title">
      <assert test="text()">
        title may not be empty
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Useful title\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title></title>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Useful title\nAssertion failure:\ntitle may not be empty\n'),
)
)

EXAMPLES += [EG_3_8]

EG_3_9 = (
'eg3_9',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Author elements">
    <rule context="author">
      <assert test="count(name|bio|affiliation) = count(*)">
        Only "name", "bio" and "affiliation" elements are allowed as children of "author"
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">
      <name>Chikezie Emereuwa</name>
      <bio>Chikezie Emereuwa is a quantum engineer and NASA researcher</bio>
      <affiliation>NASA</affiliation>
    </author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author elements\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">
      <name>Chikezie Emereuwa</name>
      <bio>Chikezie Emereuwa is a quantum engineer and NASA researcher</bio>
      <affiliation>NASA</affiliation>
      <age>39</age>
    </author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Author elements\nAssertion failure:\nOnly "name", "bio" and "affiliation" elements are allowed as children of "author"\n'),
)
)

EXAMPLES += [EG_3_9]

EG_4_1 = (
'eg4_1',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Military authors">
    <rule context="author">
      <!-- This test should really be refined so it
           checks that '.mil' is in the last position -->
      <report test="contains(@e-mail, '.mil')">
        Author appears to be military personnel
      </report>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
    <author member='yes' e-mail="okey.agu@navy.mil">Okechukwu Agu</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Military authors\nReport:\nAuthor appears to be military personnel\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Military authors\n'),
),
()
)

EXAMPLES += [EG_4_1]

EG_4_2 = (
'eg4_2',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Report links">
    <rule context="*">
      <report test="@link">
        <name/> element has a link.
      </report>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue/>
  <section>
    Placeholder for the <emphasis link='http://nasa.gov/ftl/paper.xml'>actual content</emphasis>.
  </section>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Report links\nReport:\nemphasis element has a link.\n'),
),
()
)

EXAMPLES += [EG_4_2]

EG_4_3 = (
'eg4_3',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Title with subtitle">
    <rule context="title">
      <assert test="following-sibling::*[1]/self::subtitle">
        A <name/> must be immediately followed by a "subtitle",
        not <name path="following-sibling::*[1]"/>.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\nAssertion failure:\nA title must be immediately followed by a "subtitle",\nnot .\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <midtitle>Seriously</midtitle>
    <subtitle>From fantasy to reality</subtitle>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Title with subtitle\nAssertion failure:\nA title must be immediately followed by a "subtitle",\nnot midtitle.\n'),
)
)

EXAMPLES += [EG_4_3]

EG_4_4 = (
'eg4_4',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Report links">
    <rule context="*">
      <report test="@link">
        <name/> element has a link to <value-of select="@link"/>.
      </report>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue/>
  <section>
    Placeholder for the <emphasis link='http://nasa.gov/ftl/paper.xml'>actual content</emphasis>.
  </section>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Report links\nReport:\nemphasis element has a link to http://nasa.gov/ftl/paper.xml.\n'),
),
()
)

EXAMPLES += [EG_4_4]

EG_4_5 = (
'eg4_5',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Major elements">
    <rule context="doc">
      <assert test="prologue" diagnostics="doc-struct">
        <name/> element must have a prologue.
      </assert>
      <assert test="section" diagnostics="doc-struct sect">
        <name/> element must have at least one section.
      </assert>
    </rule>
  </pattern>
  <diagnostics>
    <diagnostic id="doc-struct">
       A document (the <name/> element) must have a prologue and one or
       more sections.  Please correct your submission by adding the
       required elements, then re-submit.  For your records, the
       submission ID is <value-of select="@id"/>.
    </diagnostic>
    <diagnostic id="sect">
       Sections are sometimes omitted because authors think they can
       just place the document contents directly after the prologue.
       You may be able to correct this error by just wrapping your
       existing content in a section element.
    </diagnostic>
  </diagnostics>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc id='ftl2004'>
  <prologue/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\n'),
(u'''\
<doc id='ftl2004'>
  <prologue/>
  <section/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\n'),
),
(
(u'''\
<doc id='ftl2004'>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\ndoc element must have a prologue.\nDiagnostic message:\nA document (the doc element) must have a prologue and one or\nmore sections. Please correct your submission by adding the\nrequired elements, then re-submit. For your records, the\nsubmission ID is ftl2004.\n'),
(u'''\
<doc id='ftl2004'>
  <prologue/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\ndoc element must have at least one section.\nDiagnostic message:\nA document (the doc element) must have a prologue and one or\nmore sections. Please correct your submission by adding the\nrequired elements, then re-submit. For your records, the\nsubmission ID is ftl2004.\nDiagnostic message:\nSections are sometimes omitted because authors think they can\njust place the document contents directly after the prologue.\nYou may be able to correct this error by just wrapping your\nexisting content in a section element.\n'),
(u'''\
<doc id='ftl2004'/>
'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\ndoc element must have a prologue.\nDiagnostic message:\nA document (the doc element) must have a prologue and one or\nmore sections. Please correct your submission by adding the\nrequired elements, then re-submit. For your records, the\nsubmission ID is ftl2004.\nAssertion failure:\ndoc element must have at least one section.\nDiagnostic message:\nA document (the doc element) must have a prologue and one or\nmore sections. Please correct your submission by adding the\nrequired elements, then re-submit. For your records, the\nsubmission ID is ftl2004.\nDiagnostic message:\nSections are sometimes omitted because authors think they can\njust place the document contents directly after the prologue.\nYou may be able to correct this error by just wrapping your\nexisting content in a section element.\n')
)
)

EXAMPLES += [EG_4_5]

EG_5_1 = (
'eg5_1',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Special XHTML conventions</title>
  <ns uri="http://www.w3.org/1999/xhtml" prefix="html"/>
  <pattern name="Document head">
    <rule context="html:head">
      <assert test="html:title">Page does not have a title.</assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" type="text/css" href="std.css"/>
    <title>Document head</title>
  </head>
  <body class="std-body">
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Special XHTML conventions\nProcessing pattern: Document head\n'),
),
(
(u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" type="text/css" href="std.css"/>
  </head>
  <body class="std-body">
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Special XHTML conventions\nProcessing pattern: Document head\nAssertion failure:\nPage does not have a title.\n'),
)
)

EXAMPLES += [EG_5_1]

EG_5_2 = (
'eg5_2',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron"
        xmlns:html="http://www.w3.org/1999/xhtml">
  <title>Technical document schema</title>
  <pattern name="Major elements">
    <rule context="doc">
      <assert test="section">
        <html:p>
          <name/> must have at least one <html:code>section</html:code>
          child.
        </html:p>
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\n'),
),
(
(u'''\
<doc>
  <prologue/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Major elements\nAssertion failure:\n<p xmlns="http://www.w3.org/1999/xhtml">\ndoc must have at least one <code>section</code>\nchild.\n</p>\n'),
)
)

EXAMPLES += [EG_5_2]

EG_5_3 = (
'eg5_3',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <key name="author-e-mails" match="author" use="@e-mail"/>
  <pattern name="Main contact">
    <rule context="main-contact">
      <assert test="key('author-e-mails', @e-mail)">
        "e-mail" attribute must match the e-mail of one of the authors
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
    <author member='yes' e-mail="okey.agu@navy.mil">Okechukwu Agu</author>
    <main-contact e-mail='cemereuwa@nasa.gov'/>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Main contact\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
    <author member='yes' e-mail="okey.agu@navy.mil">Okechukwu Agu</author>
    <main-contact e-mail='info@nasa.gov'/>
  </prologue>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Main contact\nAssertion failure:\n"e-mail" attribute must match the e-mail of one of the authors\n'),
)
)

EXAMPLES += [EG_5_3]

EG_5_4 = (
'eg5_4',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <pattern name="Section minimum">
    <rule context="doc">
      <assert test="count(section) >= 3*count(prologue/author)">
        There must be at least three sections for each author.
      </assert>
    </rule>
  </pattern>
</schema>'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
  <section/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Section minimum\n'),
),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">Chikezie Emereuwa</author>
  </prologue>
  <section/>
  <section/>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Section minimum\nAssertion failure:\nThere must be at least three sections for each author.\n'),
)
)

EXAMPLES += [EG_5_4]

EG_5_5 = (
'eg5_5',
u'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Technical document schema</title>
  <key name="author-e-mails" match="author" use="@e-mail"/>
  <phase id="quick-check"> <!-- "minimal sanity check" -->
    <active pattern="rightdoc" />
  </phase>
  <phase id="full-check">
    <active pattern="rightdoc" />
    <active pattern="extradoc" />
    <active pattern="majelements" />
  </phase>
  <phase id="process-links">
    <active pattern="report-link" />
  </phase>
  <pattern id="rightdoc" name="Document root">
    <rule context="/">
      <assert test="doc">Root element must be "doc".</assert>
    </rule>
  </pattern>
  <pattern id="extradoc" name="Extraneous docs">
    <rule context="doc">
      <assert test="not(ancestor::*)">
        The "doc" element is only allowed at the document root.
      </assert>
    </rule>
  </pattern>
  <pattern id="majelements" name="Major elements">
    <rule context="doc">
      <assert test="prologue">
        <name/> must have a "prologue" child.
      </assert>
      <assert test="section">
        <name/> must have at least one "section" child.
      </assert>
    </rule>
  </pattern>
  <pattern id="report-link" name="Report links">
    <rule context="*">
      <report test="@link">
        <name/> element has a link to <value-of select="@link"/>.
      </report>
    </rule>
  </pattern>
</schema>
'''.encode(ENCODING),
(
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">
      <name>Chikezie Emereuwa</name>
      <bio>Chikezie Emereuwa is a quantum engineer and NASA researcher</bio>
      <affiliation>NASA</affiliation>
    </author>
  </prologue>
  <section>
    Actual contents may have shifted in transmission.
  </section>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nProcessing pattern: Report links\n'),
(u'''\
<doc>
  <prologue/>
  <section>
    Placeholder for the <emphasis link='http://nasa.gov/ftl/paper.xml'>actual content</emphasis>.
  </section>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nProcessing pattern: Report links\nReport:\nemphasis element has a link to http://nasa.gov/ftl/paper.xml.\n'),
),
(
(u'''\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" type="text/css" href="std.css"/>
    <title>Document head</title>
  </head>
  <body class="std-body">
    <div class="std-top">Top component</div>
  </body>
</html>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nAssertion failure:\nRoot element must be "doc".\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nProcessing pattern: Report links\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">
      <name>Chikezie Emereuwa</name>
      <bio>Chikezie Emereuwa is a quantum engineer and NASA researcher</bio>
      <affiliation>NASA</affiliation>
    </author>
  </prologue>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nAssertion failure:\ndoc must have at least one "section" child.\nProcessing pattern: Report links\n'),
(u'''\
<doc>
  <section>
    Placeholder for the <emphasis link='http://nasa.gov/ftl/paper.xml'>actual content</emphasis>.
  </section>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nAssertion failure:\ndoc must have a "prologue" child.\nProcessing pattern: Report links\nReport:\nemphasis element has a link to http://nasa.gov/ftl/paper.xml.\n'),
(u'''\
<doc>
  <prologue>
    <title>Faster than light travel</title>
    <subtitle>From fantasy to reality</subtitle>
    <author member='yes' e-mail="cemereuwa@nasa.gov">
      <name>Chikezie Emereuwa</name>
      <bio>Chikezie Emereuwa is a quantum engineer and NASA researcher</bio>
      <affiliation>NASA</affiliation>
    </author>
    <section>
      Where does the section element go again?
    </section>
  </prologue>
</doc>'''.encode(ENCODING),
'<?xml version="1.0" encoding="UTF-8"?>\nProcessing schema: Technical document schema\nProcessing pattern: Document root\nProcessing pattern: Extraneous docs\nProcessing pattern: Major elements\nAssertion failure:\ndoc must have at least one "section" child.\nProcessing pattern: Report links\n'),
)
)

EXAMPLES += [EG_5_5]


"""
EG_5_2 = (
'eg5_2',
u'''\
'''.encode(ENCODING),
(
(u'''\
'''.encode(ENCODING),
''),
),
(
(u'''\
'''.encode(ENCODING),
''),
)
)

EXAMPLES += [EG_5_2]
"""


def normalize_text(text):
    #normalize text, a bit slow for large files with much non-ws
    return reduce(lambda a, b: (a and a[-1].isspace() and b.isspace()) and a or a+b, text, '')


class TestBasics(unittest.TestCase):
    def setUp(self):
        #self.isrc_factory = InputSource.DefaultFactory
        return

    def testStrons(self):
        for (name, stron, good, bad) in EXAMPLES:
            print name
            #open(os.path.join('/tmp/stron', name+'.sch'), 'w').write(stron)
            for (count, (instance, expected)) in enumerate(good):
                output = run_stron(stron, instance)
                #print output
                #normalize text, a bit slow for large files with much non-ws
                output = normalize_text(output)
                self.assertEqual(output, expected)
                #open(os.path.join('/tmp/stron', name+'_good%i.xml'%(count+1)), 'w').write(instance)
            for (count, (instance, expected)) in enumerate(bad):
                output = run_stron(stron, instance)
                #print output
                #normalize text, a bit slow for large files with much non-ws
                output = normalize_text(output)
                self.assertEqual(output, expected)
                #open(os.path.join('/tmp/stron', name+'_bad%i.xml'%(count+1)), 'w').write(instance)
        return


if __name__ == '__main__':
    unittest.main()

