#
# The command line code executes a simple battery of tests
#
from amara import domtools
from xml.dom import Node


if __name__ == "__main__":
    #The following exercises the code as demonstrated in the article
    DOC1 = """<?xml version='1.0' encoding='iso-8859-1'?>
<verse>
  <attribution>Louis MacNeice</attribution>
  <line>The Laird o' Phelps spent Hogmanay declaring he was sober,</line>
  <line>Counted his feet to prove the fact and found he had one foot over.</line>
  <line>Mrs. Carmichael had her fifth, looked at the job with repulsion,</line>
  <line>Said to the midwife "Take it away; I'm through with overproduction."</line>
</verse>"""

    DOC2 = """<?xml version='1.0' encoding='iso-8859-1'?>
<nest>
  <bird>cheep</bird> in the
    <nest>
      <bird>cheep</bird> in the <nest>bird</nest>
    </nest>
  <nest>bird</nest> upon a <tree><nest>bird</nest></tree>
</nest>
"""

    DOC3 = """<?xml version="1.0" encoding="iso-8859-1"?>
<labels>
  <label added="2003-06-20">
    <quote>
      <!-- Mixed content -->
      <emph>Midwinter Spring</emph> is its own season&#8230;
    </quote>
    <name>Thomas Eliot</name>
    <address>
      <street>3 Prufrock Lane</street>
      <city>Stamford</city>
      <state>CT</state>
    </address>
  </label>
  <label added="2003-06-10">
    <name>Ezra Pound</name>
    <address>
      <street>45 Usura Place</street>
      <city>Hailey</city>
      <state>ID</state>
    </address>
  </label>
</labels>
    """

    from Ft.Xml.Domlette import NonvalidatingReader
    doc1 = NonvalidatingReader.parseString(DOC1, "http://dummy.ns")
    doc2 = NonvalidatingReader.parseString(DOC2, "http://dummy.ns")
    doc3 = NonvalidatingReader.parseString(DOC3, "http://dummy.ns")

    print "*"*10, "Listing 3", "*"*10
    print "Get elements by tag name:"
    for node in domtools.get_elements_by_tag_name(doc1, 'line'):
        print node
    print "Get elements by tag name ns:"
    for node in domtools.get_elements_by_tag_name_ns(doc1, None, 'line'):
        print node

    from Ft.Xml.XPath import Evaluate, Context
    from Ft.Xml.Domlette import GetAllNs

    def get_elements_by_tag_name_ns_xpath(node, name):
        #I need the context node and a set of namespace mappings
        #In case they use a QName for name e.g. ns:local
        #Use the dictionary of all namespace mappings on the given node
        context = Context.Context(node, GetAllNs(node))
        #Now do an XPath evaluation of an expression that searches
        #The descendant-or-self axis for all nodes whose name
        #matches the given
        return Evaluate(".//" + name, context=context)

    print "Get elements by tag name (XPath):"
    for node in get_elements_by_tag_name_ns_xpath(doc1, 'line'):
        print node

    def get_elements_by_tag_name_ns_raw(node, ns, local):
        if node.nodeType == Node.ELEMENT_NODE and \
           node.namespaceURI == ns and node.localName == local:
            result = [node]
        else:
            result = []
        for child in node.childNodes:
            result.extend(get_elements_by_tag_name_ns_raw(child, ns, local))
        return result

    print "Get elements by tag name (Raw recursion):"
    for node in get_elements_by_tag_name_ns_raw(doc2, None, 'nest'):
        print node

    print "abs_path test"
    print repr(domtools.abs_path(doc3))
    node = doc3.documentElement
    print repr(domtools.abs_path(node))
    node = domtools.get_first_element_by_tag_name_ns(doc3, None, 'label')
    print repr(domtools.abs_path(node))
    node = list(domtools.get_elements_by_tag_name_ns(doc3, None, 'label'))[1]
    print repr(domtools.abs_path(node))
    node = node.attributes[(None, 'added')]
    print repr(domtools.abs_path(node))

    NAME = "GAMES"
    NAME = "v"
    NAME = "LINE"
    BIG_FILE_NAMES = ["1998statistics.xml", "ot.xml", "hamlet.xml"]
    for fname in BIG_FILE_NAMES:
        try:
            big_doc = NonvalidatingReader.parseUri(fname)
        except:
            print "Unable to load", fname
            continue
        element_count = len(
            domtools.get_elements_by_tag_name_ns_raw(big_doc, None, NAME)
            )
        print "Number of", NAME, "elements found:", element_count
        import time
        start = time.time()
        for i in range(10):
            for node in domtools.get_elements_by_tag_name_ns(big_doc, None, NAME):
                pass
        end = time.time()
        print "Generator getElementsByTagNameNS: %.2f"%(end-start)

        start = time.time()
        for i in range(10):
            for node in domtools.get_elements_by_tag_name_ns_xpath(big_doc, NAME):
                pass
        end = time.time()
        print "XPath getElementsByTagNameNS: %.2f"%(end-start)

        start = time.time()
        for i in range(10):
            for node in domtools.get_elements_by_tag_name_ns_raw(big_doc, None, NAME):
                pass
        end = time.time()
        print "Raw recursion getElementsByTagNameNS: %.2f"%(end-start)


