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
#
# pushdom
#

from amara import domtools
for docfrag in domtools.pushdom('/labels/label', source='labels1.xml'):
    label = docfrag.firstChild
    name = label.xpath('string(name)')
    city = label.xpath('string(address/city)')
    if name.lower().find('eliot') != -1:
        print city.encode('utf-8')

#
# abspath
#

from amara import domtools
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Lib import Uri
file_uri = Uri.OsPathToUri('labels1.xml', attemptAbsolute=1)
doc = NonvalidatingReader.parseUri(file_uri)

print domtools.abs_path(doc)
print domtools.abs_path(doc.documentElement)
for node in doc.documentElement.childNodes:
    print domtools.abs_path(node)

