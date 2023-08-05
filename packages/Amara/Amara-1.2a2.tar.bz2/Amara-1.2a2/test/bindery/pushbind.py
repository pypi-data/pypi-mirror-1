#Tests amara.pushbind

import unittest
import cStringIO
from xml.dom import Node

import amara

XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

CONTAINER = """\
<top>
  <container id='otu'>
    <value>
      <title>kedu ka i mere</title>
      <body>Ofe nsala na atu uto</body>
    </value>
  </container>
  <container id='abuo'>
    <value>
      <title>o di mma</title>
      <body>Papa nyem ugwom, O!</body>
    </value>
  </container>
</top>
"""

class TestPushBindEventHook(unittest.TestCase):

    #Disabled until Saxlette synchronicity issues are tackled
    def testContainerExample(self):
        class container_tracker:
            def startElementNS(self, name, qname, attribs):
                if name[1] == u'container':
                    #print attribs.get((None, u'id'))
                    self.id = attribs.get((None, u'id'))

        context = container_tracker()
        check = []
        for node in amara.pushbind(CONTAINER, u'value', event_hook=context):
            #print repr(node)
            #print unicode(node.title)
            check.append((context.id, unicode(node.title)))

        EXPECTED = [(u'otu', u'kedu ka i mere'), (u'abuo', u'o di mma')]
        self.assertEqual(check, EXPECTED)
        return


if __name__ == '__main__':
    unittest.main()

