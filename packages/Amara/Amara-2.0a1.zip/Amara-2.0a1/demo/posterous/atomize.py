import sys, time
import cStringIO
import datetime

import feedparser
import html5lib

from amara import bindery
from amara.bindery import html
from amara import xml_print
from amara.writers.struct import *
from amara.namespaces import *
from amara import tree

FEEDEXTRAS = E(u'name',
    E(u'title', u'Uche Ogbuji'),
    E(u'uri', u'http://uche.ogbuji.net'),
    E(u'email', u'uche@ogbuji.net'),
)

SOURCE = sys.argv[1] #Example: "http://uche.posterous.com/rss.xml"
channel = bindery.parse(SOURCE).rss.channel
html_parser = html5lib.HTMLParser(tree=html.treebuilder)

def tagsoup2struct(soup):
    s = cStringIO.StringIO(soup)
    body = html_parser.parse(s).html.body

    #Remove the stock paras (including permalink) at the end of each entry
    paras = list(body.p)
    paras.reverse()
    body.xml_remove(paras[0])
    for p in paras[1:]:
        if len(p.xml_children):
            break
        else:
            body.xml_remove(p)

    def tostruct(e):
        def handle_children(e):
            for child in e.xml_children:
                if child.xml_type == tree.element.xml_type:
                    yield tostruct(child)
                elif child.xml_type == tree.text.xml_type:
                    yield child.xml_value
                elif isinstance(child, unicode):
                    yield child
        return E(e.xml_qname, dict(e.xml_attributes.items()), ( c for c in handle_children(e)) )
    return ( tostruct(e) for e in body.xml_element_children() )


#print >> sys.stderr, "Processing "; xml_print(channel.title, stream=sys.stderr)

w = structwriter(indent=u"yes")
w.feed(
ROOT(
    E((ATOM_NAMESPACE, u'feed'), {(XML_NAMESPACE, u'xml:lang'): u'en'},
        E(u'id', SOURCE),
        E(u'title', channel.title),
        E(u'content', channel.description),
        E(u'updated', datetime.datetime.now().isoformat()),
        FEEDEXTRAS,
        #E(u'link', {u'href': u'/blog/atom1.0', u'rel': u'self'}),
        ( E(u'entry',
            E(u'id', it.guid),
            E(u'title', it.title),
            E(u'link', {u'href': it.link}),
            E(u'updated', time.strftime("%Y-%m-%dT%H:%M:%S", feedparser._parse_date(str(it.pubDate)))),
            E(u'content', {u'type': u'xhtml'},
                E((XHTML_NAMESPACE, u'div'),
                    tagsoup2struct(str(it.description))
                )
            )
        ) for it in channel.item )
    )
))
