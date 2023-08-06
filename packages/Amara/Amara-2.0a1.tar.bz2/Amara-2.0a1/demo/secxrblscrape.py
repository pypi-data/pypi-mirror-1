import sys
import sgmllib
from amara.bindery import html
from amara.lib import inputsource
from amara.writers.struct import *
from amara.namespaces import *
from amara.lib.xmlstring import *

class sec_parser(sgmllib.SGMLParser):
    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.in_xbrl = False
        self.xbrls = {}
        self._curr_fname = None
        return

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()
        return

    def do_filename(self, attrs):
        self._curr_fname = []
        return

    def unknown_starttag(self, name, attrs):
        if isinstance(self._curr_fname, list):
            self._curr_fname = ''.join(self._curr_fname).strip()
        return

    def start_xbrl(self, attrs):
        self._curr_xbrl = []
        self.setliteral()
        self.in_xbrl = True
        return

    def handle_data(self, data):
        if self.in_xbrl:
            self._curr_xbrl.append(data)
        elif isinstance(self._curr_fname, list):
            self._curr_fname.append(data)
        return

    def end_xbrl(self):
        self.in_xbrl = False
        self.xbrls[self._curr_fname] = ''.join(self._curr_xbrl).lstrip()
        return

#bindery.parse


if __name__ == '__main__':
    source = sys.argv[1]
    myparser = sec_parser()
    text = inputsource(source, None).stream.read()
    text = text[text.find('<SEC-DOCUMENT>'):text.rfind('</SEC-DOCUMENT>')]
    myparser.parse(text)
    for k, v in myparser.xbrls.iteritems():
        print k, v[:500]

