"""
Split an XML file into multiple smaller files, as described in the query
http://groups.google.com/groups?dq=&hl=en&lr=&ie=UTF-8&group=comp.lang.python&selm=fa538331.0402120759.44f20301%40posting.google.com

Specifically, put each top-level folder in an XBEL file into a separate
file--temporary files for purposes of demo
"""

#Actual demo starts 12 lines below...
import sys
import os
#Make sure we can find needed source files
if not os.access('monty.xml', os.F_OK):
    os.chdir('..')
    if not os.access('monty.xml', os.F_OK):
        print "This file is meant to be run from the demo directory (e.g. same directory as 'monty.xml' or in the demo/bindery directory"
        sys.exit(1)

#Actual demo starts here
from amara import binderytools
binding = binderytools.bind_file('xbel.xml')

#File splitting task
import tempfile

#The direct approach
for folder in binding.xbel.folder:
    fname = tempfile.mktemp('.xml')
    fout = open(fname, 'w')
    folder.xml(fout)
    fout.close()
    print 'Folder saved as ', fname


#To use XPath replace the line
#for folder in binding.xbel.folder:
#With
#for folder in binding.xml_xpath(u'xbel/folder'):

