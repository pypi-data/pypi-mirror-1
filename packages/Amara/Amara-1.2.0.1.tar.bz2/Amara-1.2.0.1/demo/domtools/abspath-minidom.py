#Actual demo starts 12 lines below...
import sys
import os
#Make sure we can find needed source files
if not os.access('monty.xml', os.F_OK):
    os.chdir('..')
    if not os.access('monty.xml', os.F_OK):
        print "This file is meant to be run from the demo directory (e.g. same directory as 'monty.xml' or in the demo/bindery directory"
        sys.exit(1)

#Actual demo starts here:
from amara import domtools
from xml.dom import minidom
doc = minidom.parse('labels1.xml')

#The rest is DOM-agnostic
print domtools.abs_path(doc)
print domtools.abs_path(doc.documentElement)
for node in doc.documentElement.childNodes:
    print domtools.abs_path(node)

