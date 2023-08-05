"""
Use the command line tidy to grab well-formed XHTML as a bindery
"""

import os
import urllib
import sys
from amara.binderytools import *

NS = {u'html': u'http://www.w3.org/1999/xhtml'}
CMDLINES = [
    'java -jar tagsoup.jar',
    'tidy -nq -asxhtml'
    ]

def tidy_bind_url(url, rules=None, binderobj=None, prefixes=None):
    #Add in a prefixed version of the namespace as well, for easier XPath
    prefixes = prefixes or {}
    prefixes.update(NS)
    for cmd in CMDLINES:
        try:
            #print >> sys.stderr, "Trying", cmd
            stream = urllib.urlopen(url)
            pin, pout = os.popen2(cmd)
            pin.write(stream.read())
            pin.close()
            break
        except IOError:
            pass
    doc = pout.read()
    binding = bind_string(doc, url, rules=rules, binderobj=binderobj, prefixes=prefixes)
    return binding


if __name__ == '__main__':
    #Sample usage
    #Internal link checker
    #url = "http://www.w3.org/TR/REC-xml" #XML spec
    #Uche's "Detailed cross-reference of the most important XML standards"
    url = "http://www.ibm.com/developerworks/xml/library/x-stand4/"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    doc = tidy_bind_url(url)
    all_links = doc.xml_xpath(u'//html:a[@href]')
    all_anchors = doc.xml_xpath(u'//html:a[@name]')
    anchor_names = [ a.name for a in all_anchors ]
    internal_refs = [ a.href for a in all_links if a.href.startswith(u'#') ]
    for ref in internal_refs:
        if ref[1:] in anchor_names:
            print ref, "valid"
        else:
            print ref, "invalid"

if False:
    #Another example, change "False" to "True" above to enable
    url = "http://webjay.org/by/chromegat/theclassicnaijajukebox2823229"
    doc = tidy_bind_url(url)
    #Display all links to mp3s (by file extension check)
    links = doc.xml_xpath(u'//html:a[@href]')
    for link in links:
        if link.href.endswith(u'.mp3'):
            print link.href

