import unittest
from xml.dom import Node
from amara import domtools
from Ft.Xml import Parse

abs_path = domtools.abs_path
parse = Parse

#Below here should be identical to ../bindery/tools.py

class TestSB060223(unittest.TestCase):
    #Samuel L Bayer pointed out definciencies in the namespace handling
    #of domtools.abs_path
    #http://lists.fourthought.com/pipermail/4suite/2006-February/007757.html
    XML1 = '<foo xmlns:bar="http://bar.com"><baz/><bar:baz/></foo>'
    XML2 = '<foo xmlns="http://bax.com" xmlns:bar="http://bar.com"><baz/><bar:baz/></foo>'
    
    def testAbsPathWithNs(self):
        doc = parse(self.XML1)
        ap = abs_path(doc.documentElement.firstChild)
        self.assertEqual(ap, u'/foo[1]/baz[1]')
        ap = abs_path(doc.documentElement.firstChild.nextSibling)
        self.assertEqual(ap, u'/foo[1]/bar:baz[1]')
        return

    def testAbsPathWithDefaultNs(self):
        doc = parse(self.XML2)
        ap = abs_path(doc.documentElement.firstChild)
        self.assertEqual(ap, u'/amara.4suite.org.ns1:foo[1]/amara.4suite.org.ns1:baz[1]')
        ap = abs_path(doc.documentElement.firstChild.nextSibling)
        self.assertEqual(ap, u'/amara.4suite.org.ns1:foo[1]/bar:baz[1]')
        ap = abs_path(doc.documentElement.firstChild, {u'bax': u'http://bax.com'})
        self.assertEqual(ap, u'/bax:foo[1]/bax:baz[1]')
        ap = abs_path(doc.documentElement.firstChild.nextSibling, {u'bax': u'http://bax.com'})
        self.assertEqual(ap, u'/bax:foo[1]/bar:baz[1]')
        return


if __name__ == '__main__':
    unittest.main()

