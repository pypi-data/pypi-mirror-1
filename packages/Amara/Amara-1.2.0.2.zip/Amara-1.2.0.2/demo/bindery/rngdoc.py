#IGNORE FOR NOW

"""
Create HTML docs and index from a set of RELAX NG files
"""

import sys
import os
import re
from amara import binderytools

rng_dir = sys.argv[1]
output_file = open(sys.argv[2], 'w')
RNG_FILE_PAT = re.compile('.*\.rng')

PREFIXES = {
    'rng': 'http://relaxng.org/ns/structure/1.0',
    'ega': 'http://examplotron.org/annotations/'
}

from Ft.Xml.Xslt.XmlWriter import XmlWriter
#from Ft.Xml.Xslt.HtmlWriter import HtmlWriter
from Ft.Xml.Xslt.OutputParameters import OutputParameters


class define(object):
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.attributes = []
        self.text_patterns = []
        self.xhtml_fragment = ''

class namespace(object):
    def __init__(self, name):
        self.uri = uri
        self.prefix = prefix
        self.elements = []
        self.attributes = []
        self.xhtml_fragment = ''

class attribute(object):
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.attributes = []
        self.text_patterns = []
        self.xhtml_fragment = ''

class element(object):
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.attributes = []
        self.text_patterns = []
        self.xhtml_fragment = ''

class rngdoc:
def process_rng(path, writer):
    container = binderytools.bind_file(path, prefixes=PREFIXES)
    for define in container.xml_xpath('//rng:define'):
        print define.name
        pass
    #container.xml_xpath(u'//rng:externalRef')
    return


oparams = OutputParameters()
oparams.indent = 'yes'
writer = XmlWriter(oparams, output_file)
writer.startDocument()

for cdir, subdirs, files in os.walk(rng_dir):
    #print "Processing:", cdir, subdirs, files
    for fname in files:
        #if fname.endsWith('.rng')
        if RNG_FILE_PAT.match(fname):
            path = os.path.join(cdir, fname)
            print 'Processing', path
            process_rng(path, writer)

writer.endDocument()

