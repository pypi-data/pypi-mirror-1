"""
Examples of sax2dom_chunker in action.
Don't forget amara.domtools.pushdom, with which you could
reduce this entire file to about 10 lines
"""

from Ft.Xml import Sax
from Ft.Lib import Uri
from amara.saxtools import sax2dom_chunker

#Example 1: Print out all the cities in which someone named "Eliot" lives


SEARCH_FOR_STRING = 'eliot'

def process_label(docfrag):
    #Invoked for each label
    label = docfrag.firstChild
    name = label.xpath('string(name)')
    city = label.xpath('string(address/city)')
    if name.lower().find(SEARCH_FOR_STRING) != -1:
        print city.encode('utf-8')
    return

#The path for chunking by label element
#Equivalent to the XPattern /labels/label
LABEL_PATH = [ (None, u'labels'),  (None, u'label') ]

#Create an instance of the chunker
handler = sax2dom_chunker(
    xpatterns=['/labels/label'],
    chunk_consumer=process_label
    )

parser = Sax.CreateParser()

#The chunker is the SAX handler
parser.setContentHandler(handler)
parser.parse(Uri.OsPathToUri('../labels1.xml'))

#
#Example 2: Print out all people and their street address
#

PATHS = ['/labels/label/name', '/labels/label/address/street']

def process_chunk(docfrag):
    #Invoked for each name or address.  We're getting the leaf element
    #of the path itself (in a doc frag wrapper) so just print its text
    #content
    text = docfrag.firstChild.firstChild.data
    print text.encode('utf-8')
    return


#Create an instance of the chunker
handler = sax2dom_chunker(
    xpatterns=PATHS,
    chunk_consumer=process_chunk
    )

parser = Sax.CreateParser()

#The chunker is the SAX handler
parser.setContentHandler(handler)
parser.parse(Uri.OsPathToUri('../labels1.xml'))

#
#Example 3: Print out all the cities in which someone named "Eliot" lives
#

PROD_NS = 'http://example.com/product-info'
XHTML_NS = 'http://www.w3.org/1999/xhtml'
SEARCH_FOR_STRING = 'python'

def process_product(docfrag):
    #Invoked for each product
    product = docfrag.firstChild
    desc = product.xpath('string(.//p:description[1])',
                         explicitNss={'p': PROD_NS})
    if desc.lower().find(SEARCH_FOR_STRING) != -1:
        print product.getAttributeNS(None, u'id').encode('utf-8')
    return

#The path for chunking by label element
#Equivalent to the XPattern /products/p:product
PROD_PATH = [ u'products/p:product']

#Create an instance of the chunker
handler = sax2dom_chunker(
    xpatterns=PROD_PATH,
    nss={u'p': PROD_NS},
    chunk_consumer=process_product
    )

parser = Sax.CreateParser()

#The chunker is the SAX handler
parser.setContentHandler(handler)

parser.parse(Uri.OsPathToUri('../products.xml'))
#doc = handler.get_root_node()
#from Ft.Xml.Domlette import Print
#Print(doc)

