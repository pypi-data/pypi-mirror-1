#Tests examples given in the manual

import unittest
import amara
from amara import bindery, binderytools
from Ft.Xml import InputSource
from Ft.Lib import Uri

XBEL_PATH = "../../demo/xbel.xml"

class TestManualExamples(unittest.TestCase):
    def setUp(self):
        #Really not used, yet
        self.isrc_factory = InputSource.DefaultFactory
        return

    def _input_source_for_file(self, fname):
        #Create a URI from a filename the right way
        file_uri = Uri.OsPathToUri(fname, attemptAbsolute=1)
        isrc = self.isrc_factory.fromUri(file_uri)
        return isrc

    def testElementPresence(self):
        #isrc = self._input_source_for_file(XBEL_PATH)
        binding = amara.parse(XBEL_PATH)
        self.assertEqual(len(list(binding.xbel)), 1)
        self.assert_(hasattr(binding, 'xbel'))
        self.assertEqual(len(list(binding.xbel.title)), 1)
        self.assert_(hasattr(binding.xbel, 'title'))
        self.assertEqual(len(list(binding.xbel.folder)), 3)
        self.assert_(hasattr(binding.xbel, 'folder'))
        self.assert_(hasattr(binding.xbel.folder, 'title'))
        self.assert_(hasattr(binding.xbel.folder, 'bookmark'))
        self.assert_(hasattr(binding.xbel.folder[1], 'folder'))
        self.assert_(hasattr(binding.xbel.folder.bookmark, 'title'))
        #self.assertEqual(binding.xbel)
        #self.assertRaises(AttributeError, binding.xbel.folder.)
        return

    def testAttributes(self):
        binding = amara.parse(XBEL_PATH)
        self.assert_(hasattr(binding.xbel.folder.bookmark, 'href'))
        self.assertEqual(binding.xbel.folder.bookmark.href, u'http://4suite.org/')
        return

    def testContent(self):
        binding = amara.parse(XBEL_PATH)
        self.assertEqual(unicode(binding.xbel.title), u'Some 4Suite Bookmarks')
        self.assertEqual(unicode(binding.xbel.folder.title), u'Main links')
        self.assertEqual(unicode(binding.xbel.folder.bookmark.title), u'4Suite home page')
        self.assertEqual(len(binding.xbel.folder.bookmark.xml_children), 3)
        self.assertEqual(unicode(binding.xbel.folder.bookmark), u'\n      4Suite home page\n    ')
        self.assertEqual(binding.xbel.folder.bookmark.xml_child_text, u'\n      \n    ')
        self.assertEqual(binding.xbel.folder.bookmark.xml_children[0], u'\n      ')
        return

    def testWsStripElementRule(self):
        strip = [u"/*"]
        custom_rule = binderytools.ws_strip_element_rule(strip)
        binder = bindery.binder()
        binder.preserve_comments = True
        binding = amara.parse(XBEL_PATH, rules=[custom_rule], binderobj=binder)
        #binder.add_rule(custom_rule)
        #binding = binder.read_xml(isrc)
        self.assertEqual(len(binding.xbel.xml_children), 5)
        return


if __name__ == '__main__':
    unittest.main()

