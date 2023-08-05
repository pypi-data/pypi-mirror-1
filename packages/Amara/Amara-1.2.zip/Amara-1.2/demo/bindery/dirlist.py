#Uses Amara to print an XML file containing the directory/file subtree within
#A given path
#See http://copia.ogbuji.net/blog/2005-05-09/XML_recurs

import os
import sys
from amara import binderytools

root = sys.argv[1]

doc = binderytools.create_document()
name = unicode(root)
doc.xml_append(
    doc.xml_element(u'directory', attributes={u'name': name})
)
dirs = {root: doc.directory}

for cdir, subdirs, files in os.walk(root):
    cdir_elem = dirs[cdir]
    name = unicode(cdir)
    for f in files:
        name = unicode(f)
        cdir_elem.xml_append(
            doc.xml_element(u'file', attributes={u'name': name})
            )
    for subdir in subdirs:
        full_subdir = os.path.join(root, subdir)
        name = unicode(full_subdir)
        subdir_elem = doc.xml_element(u'directory',
                                      attributes={u'name': name})
        cdir_elem.xml_append(subdir_elem)
        dirs[full_subdir] = subdir_elem

print doc.xml(indent=u"yes")  #Print it

