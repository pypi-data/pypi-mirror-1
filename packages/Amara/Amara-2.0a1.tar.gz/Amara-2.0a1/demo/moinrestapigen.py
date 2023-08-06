# -*- coding: iso-8859-1 -*-
"""
moinrestapigen.py

A tool to generate RESTful API wrappers for MoinMoin wikis

@copyright: 2009 by Uche ogbuji <uche@ogbuji.net>

This is a code generator that combines basic knowledge of MoinMoin wiki forms and
structure with some site analysis to generate a library that supports
wrapping a Wiki instance with a REST interface.

Sample usage:
    moinrestapigen http://localhost:8080/FooTest FooTest
"""

import amara
from amara import bindery
from amara.writers.struct import *
from amara.bindery.html import parse as htmlparse

SKEL = """
from string import Template

"""

def moinrestapigen(link, pagename):
    doc = htmlparse(link)
    rawlink_code = 'RAWLINK_TPL = Template()'
    """
    <html><head><title>$title</title></head><body>
    $body
    </body></html>
    """)
    
    return


#Ideas borrowed from
# http://www.artima.com/forums/flat.jsp?forum=106&thread=4829

def command_line_prep():
    from optparse import OptionParser
    usage = "%prog [options] source cmd"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--normalize",
                      action="store_false", dest="normalize", default=-False,
                      help="send a normalized version of the Atom to the console")
    #parser.add_option("-q", "--quiet",
    #                  action="store_false", dest="verbose", default=1,
    #                  help="don't print status messages to stdout", metavar="<PREFIX=URI>")
    return parser


def main(argv=None):
    #But with better integration of entry points
    if argv is None:
        argv = sys.argv
    # By default, optparse usage errors are terminated by SystemExit
    try:
        optparser = command_line_prep()
        options, args = optparser.parse_args(argv[1:])
        # Process mandatory arguments with IndexError try...except blocks
        try:
            source = args[0]
        except IndexError:
            optparser.error("Missing filename/URL to parse")
        #try:
        #    xpattern = args[1]
        #except IndexError:
        #    optparser.error("Missing main xpattern")
    except SystemExit, status:
        return status

    # Perform additional setup work here before dispatching to run()
    # Detectable errors encountered here should be handled and a status
    # code of 1 should be returned. Note, this would be the default code
    # for a SystemExit exception with a string message.

    #try:
    #    xpath = args[2].decode('utf-8')
    #except IndexError:
    #    xpath = None
    #xpattern = xpattern.decode('utf-8')
    #sentinel = options.sentinel and options.sentinel.decode('utf-8')
    #display = options.display and options.display.decode('utf-8')
    #prefixes = options.ns
    #limit = options.limit
    #if source == '-':
    #    source = sys.stdin
    print options.normalize
    #run(source, xpattern, xpath, limit, sentinel, display, prefixes)
    if options.test:
        test()
    else:
        moinrestapigen(link)#, options.normalize)
    return


if __name__ == "__main__":
    sys.exit(main(sys.argv))






import sys, time
import datetime
import cStringIO
import feedparser
from itertools import *

import simplejson

def get_data_from_page(entry, link):
    page = htmlparse(link)
    entry['authors'] = [ unicode(m.content) for m in page.html.head.meta if m.xml_select(u'string(@name)') == u"dc.Contributor" ]
    buf = cStringIO.StringIO()
    amara.xml_print(page.html.body.xml_select(u'//*[@src="http://www.jove.com//resources/VideoPlayer/AC_RunActiveContent.js"]')[0].xml_parent, buf)
    entry['media_code'] = buf.getvalue()
    #print [ (m, unicode(m.xml_select(u'@name'))) for m in page.html.head.meta ]
    return entry


PFEED = "http://feeds.feedburner.com/jove"
feed = bindery.parse(PFEED)

entries = []

for it in islice(feed.rss.channel.item, 0, 3):
    entry = {}
    print "processing", unicode(it.link)
    entry['id'] = unicode(it.link)
    entry['label'] = entry['id']
    entry['title'] = unicode(it.title)
    entry['description'] = unicode(it.description)
    entry['link'] = unicode(it.origLink)
    entry['pubDate'] =time.strftime("%Y-%m-%dT%H:%M:%S", feedparser._parse_date(str(it.pubDate)))
    entry['categories'] = [ unicode(c) for c in it.category ]
    entry = get_data_from_page(entry, str(it.origLink))
    entries.append(entry)

print simplejson.dumps({'items': entries}, indent=4)


sys.exit(0)

w = structwriter(indent=u"yes")
w.feed(
ROOT(
    E(u'div',
        ( E(u'a', {u'href': unicode(it.link)}, unicode(it.title))
          for it in feed.rss.channel.item ),
    )
))

