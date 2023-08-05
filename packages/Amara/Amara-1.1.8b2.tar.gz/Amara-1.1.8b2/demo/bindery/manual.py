#Actual demo starts 12 lines below...
import os, sys
#Make sure we can find needed source files
if not os.access('monty.xml', os.F_OK):
    os.chdir('..')
    if not os.access('monty.xml', os.F_OK):
        print "This file is meant to be run from the demo directory (e.g. same directory as 'monty.xml' or in the demo/bindery directory"
        sys.exit(1)

#Actual demo starts here:
import amara
from amara import binderytools
doc = amara.parse('monty.xml')
print doc.monty.python.spam
print doc.monty.python[1]

#

doc = amara.parse('xbel.xml')
print doc.xbel.folder.bookmark.title
print doc.xbel.folder.bookmark[1].title

print doc.xbel.folder.bookmark.title
print doc.xbel.folder.bookmark[0].title
print unicode(doc.xbel.folder.bookmark.title)
print unicode(doc.xbel.folder.bookmark[0].title)
print doc.xbel.folder.bookmark.title.xml_text_content()
print doc.xbel.folder.bookmark.title[0].xml_text_content()

"""Cut from manual, but still demoed here:
There is a subtelty in that the first two forms are actually passing
Bindery objects to print.  Bindery objects know how to print themselves,
so you don't generally notice this.  The last four lines on the other
hand pass Python Unicode objects to print.  If you want to get a sense of
Bindery under the covers, Use the repr() function to wrap the values being
printed.
"""

print repr(doc.xbel.folder.bookmark.title)
print repr(doc.xbel.folder.bookmark[0].title)
print repr(unicode(doc.xbel.folder.bookmark.title))
print repr(unicode(doc.xbel.folder.bookmark[0].title))
print repr(doc.xbel.folder.bookmark.title.xml_text_content())
print repr(doc.xbel.folder.bookmark.title[0].xml_text_content())

print unicode(doc.xbel.folder.bookmark.title).encode('utf-8')

#
#Print all bookmark hrefs
#

def all_titles_in_folder(folder):
    for bookmark in folder.bookmark:
            print bookmark.href
    if hasattr(folder, "folder"):
        #There are sub-folders
        for folder in folder.folder:
            all_titles_in_folder(folder)
    return

for folder in doc.xbel.folder:
    all_titles_in_folder(folder)

print doc.xml() #write back out as XML to the console
print doc.xbel.folder.xml() #Just the first folder
doc.xml(sys.stdout) #write back out as XML to the console

from Ft.Xml.Xslt.XmlWriter import XmlWriter
from Ft.Xml.Xslt.OutputParameters import OutputParameters

oparams = OutputParameters()
oparams.indent = 'yes'
oparams.encoding = 'iso-8859-1'
writer = XmlWriter(oparams, sys.stdout)

#If you're serializing anything but a full document, you must
#explicitly call writer.startDocument() ... writer.endDocument()
doc.xml(writer=writer)

#
# XPath
#

print
tl_folders = doc.xbel.xml_xpath(u'folder')
for folder in tl_folders:
    print folder.title.xml_text_content()

r = doc.xbel.folder.bookmark[0].xml_xpath(u'*[1]')
r = doc.xbel.folder.bookmark.xml_xpath(u'*[1]')
r = doc.xbel.xml_xpath(u'folder[1]/bookmark[1]/*[1]')
r = doc.xbel.xml_xpath(u'/folder[1]/bookmark[1]/*[1]')
r = doc.xml_xpath(u'xbel/folder[1]/bookmark[1]/*[1]')

print r[0]

bookmarks = doc.xml_xpath(u'//bookmark')
for bookmark in bookmarks:
    print bookmark.href

hrefs = doc.xml_xpath(u'//@href')
for href in hrefs:
    print unicode(href)

url = u"http://4suite.org/"

#
# Namespaces
#

#Set up customary namespace bindings for RSS
#These are used in XPath query and XPattern rules
RSS10_NSS = {
    u'rdf': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    u'dc': u'http://purl.org/dc/elements/1.1/',
    u'rss': u'http://purl.org/rss/1.0/',
    }

doc = amara.parse('rss10.rdf', prefixes=RSS10_NSS)

#Create a dictionary of RSS items
items = {}
item_list = doc.xml_xpath(u'//rss:item')
items = dict( [ ( item.about, item) for item in item_list ] )
print items

for channel in doc.RDF.channel:
    print "Channel:", channel.about
    print "Title:", channel.title
    print "Items:"
    for item_ref in channel.items.Seq.li:
        item = items[item_ref.resource]
        print "\t", item.link
        print "\t", item.title

#Show the namespace particulars of the rdf:RDF element
print doc.RDF.namespaceURI
print doc.RDF.localName
print doc.RDF.prefix

#Get the RSS item with a given URL
item_url = u'http://www.oreillynet.com/cs/weblog/view/wlg/532'
matching_items = doc.xml_xpath(u'//rss:item[@rdf:about="%s"]'%item_url)
print matching_items
assert matching_items[0].about == item_url

#
# Modification
#

doc = amara.parse('monty.xml')
doc.monty.foo = u'bar'

doc.monty.python.xml_clear()
print doc.xml()

doc.monty.python.xml_append(doc.xml_element(None, u'new'))
doc.monty.python.new.xml_children.append(u'New Content')
print doc.xml()

print doc.monty.xml_children
ix = doc.monty.python.xml_index_on_parent()  #ix = 2
print ix
ix = doc.monty.python[1].xml_index_on_parent()  #ix = 5
print ix
doc.monty.xml_remove_child(ix)
print doc.xml()

#
# Customizing the binding
#

#
# Treating some elements as simple string values
#

import amara
from amara import binderytools
from amara import bindery

#Specify (using XPatterns) elements to be treated similarly to attributes
rules = [
    binderytools.simple_string_element_rule(u'title')
    ]
#Execute the binding
doc = amara.parse('xbel.xml', rules=rules)

#Print the title
print doc.xbel.folder.bookmark.title
print repr(doc.xbel.folder.bookmark.title)

#Same operation, but different approach

#Explicitly create a binder instance, in order to customize rules
binder = bindery.binder()
custom_rule = binderytools.simple_string_element_rule(u'title')
binder.add_rule(custom_rule)

#Execute the binding
doc = amara.parse('xbel.xml', binderobj=binder)

#Print the title
print doc.xbel.folder.bookmark.title
print repr(doc.xbel.folder.bookmark.title)


#
# Omitting some elements altogether
#

import amara
from amara import binderytools
from amara import bindery
#Explicitly create a binder instance, in order to customize rules
binder = bindery.binder()

#Specify (using XPatterns) elements to be omitted
rules = [
    binderytools.omit_element_rule(u"folder/title")
    ]
#Execute the binding
doc = amara.parse('xbel.xml', rules=rules)

#Folder titlees should be missing
try:
    print doc.xbel.folder.title
except AttributeError:
    print "AttributeError accessing doc.xbel.folder.title, as expected"
#But bookmark title should be there
print doc.xbel.folder.bookmark.title
print repr(doc.xbel.folder.bookmark.title)
doc.xml(sys.stdout)
print
print

#
# White-space stripping
#

import amara
from amara import binderytools
from amara import bindery
#Explicitly create a binder instance, in order to customize rules
binder = bindery.binder()

#Specify (using XPatterns) elements to be omitted
rules = [
    binderytools.ws_strip_element_rule(u"*")
    ]
#Execute the binding
doc = amara.parse('xbel.xml', rules=rules)

#doc.xbel.folder.title
doc.xml(sys.stdout)


#
# More detail-oriented binding API
#

import amara
from amara import binderytools
from amara import bindery
from Ft.Xml import InputSource
from Ft.Lib import Uri

#Create an input source for the XML
isrc_factory = InputSource.DefaultFactory
#Create a URI from a filename the right way
file_uri = Uri.OsPathToUri("xbel.xml", attemptAbsolute=1)
isrc = isrc_factory.fromUri(file_uri)

#Now bind from the XML given in the input source
binder = bindery.binder()

#Specify (using XPatterns) elements to be treated similarly to attributes
custom_rule = binderytools.simple_string_element_rule(u'title')
binder.add_rule(custom_rule)

#Bind
doc = binder.read_xml(isrc)

#xml_text_content() or str() no longer necessary to extract the text
print isinstance(doc.xbel.folder.bookmark.title, unicode)
print doc.xbel.folder.bookmark.title


#
# Use your own class for binding a given element
#

import urllib
from xml.dom import Node
from amara import binderytools
from amara import bindery
from Ft.Xml import InputSource
from Ft.Lib import Uri

#Subclass from the default binding class
#We're adding a specialized method for accessing a bookmark on the net
class specialized_bookmark(bindery.element_base):
    def retrieve(self):
        try:
            stream = urllib.urlopen(self.href)
            content = stream.read()
            stream.close()
            return content
        except IOError:
            import sys; sys.stderr.write("Unable to access %s\n"%self.href)

#Explicitly create a binder instance, in order to customize rules
binder = bindery.binder()

#associate specialized_bookmark class with elements not in an XML
#namespace and having a GI of "bookmark"
binder.set_binding_class(None, "bookmark", specialized_bookmark)

#Execute the binding
doc = amara.parse('xbel.xml', binderobj=binder)

#Show specialized instance
print doc.xbel.folder.bookmark.__class__

#Exercise the custom method
print "Content of first bookmark:"
print doc.xbel.folder.bookmark.retrieve()

print "="*72
print "RSS 1.0"
print "="*72

#
# Namespaces in XPattern-customized bindings
#

#Set up customary namespace bindings for RSS
#These are used in XPath query and XPattern rules
RSS10_NSS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'rss': 'http://purl.org/rss/1.0/',
    }

#Treat rss title, and link elements, and all DC elements as simple attributes
#BTW, simplify = [u"rss:title|rss:link|dc:*"] would work the same
simplify = [u"rss:title", u"rss:link", u"dc:*"]
custom_rule = binderytools.simple_string_element_rule(simplify)

doc = amara.parse('rss10.rdf', rules=[custom_rule], prefixes=RSS10_NSS)

#Create a dictionary of RSS items
items = {}
item_list = doc.xml_xpath(u'//rss:item')
for item in item_list:
    items[item.about] = item
print items

for channel in doc.RDF.channel:
    print "Channel:", channel.about
    print "Title:", channel.title
    print "Items:"
    for item_ref in channel.items.Seq.li:
        item = items[item_ref.resource]
        print "\t", item.link
        print "\t", item.title

#Show the namespace particulars of the rdf:RDF element
print doc.RDF.channel.title
print doc.RDF.channel.title.__class__ #Should be UNicode

for folder in amara.pushbind('xbel.xml', u'/xbel/folder'):
    title = folder.title
    bm_count = len(list(folder.bookmark))
    print "Folder", title, "has", bm_count, "top level bookmarks"


