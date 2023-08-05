"""
Demonstrate sibling grouping, a common PITA problem.
Specifically inspired by:
http://mail.python.org/pipermail/xml-sig/2005-March/011028.html
"""
import amara

XML="""\
<doc>
  <a id="1"/>
  <b id="1.1"/>
  <c id="1.2"/>
  <a id="2"/>
  <b id="2.1"/>
  <c id="2.2"/>
  <a id="3"/>
  <b id="3.1"/>
  <c id="3.2"/>
</doc>
"""

top = amara.create_document(u"doc")

container = None
for e in amara.pushbind(XML, u'/doc/*'):
    if e.nodeName == u"a":
        container = e
        top.doc.xml_append(e)
    else:
        container.xml_append(e)

print top.xml(indent=u"yes")

