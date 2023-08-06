#!/usr/bin/env python
# encoding: utf-8
"""
skosbrowser.py -- a simple server using elements from Akara to provide a first cut of transform
services for Remix

Requires: CherryPy 3.1.x ("easy_install cherrypy")

Created by Uche Ogbuji on 2008-10-15.
Copyright 2008 Zepheira LLC <http://zepheira.com>
"""

import sys, getopt, cStringIO
import cherrypy
import amara

from amara import writer
from amara.writers.struct import *
from amara.namespaces import *

help_message = '''
python skosbrowser.py <skosfile-or-uri> <baseuri>
'''

class skos_handler:
    def __init__(self, doc, baseuri, default_concept=None):
        self.doc = doc
        self.baseuri = unicode(baseuri)
        self.default_concept = doc.xml_select(u'string(//skos:Concept[1]/@rdf:about)')
        self.default_concept = self.default_concept.lstrip(self.baseuri)
        #print 'default_concept', self.default_concept
        return

    @cherrypy.expose
    def default(self, concept=None):
        if not concept: concept = self.default_concept
        #w = structwriter(indent=u"yes").feed(
        #print self.baseuri+concept
        node = self.doc.xml_select(u'//skos:Concept[@rdf:about="%s"]'%(self.baseuri+concept))[0]
        buf = cStringIO.StringIO()
        structwriter(stream=buf, is_html=True).feed(
        ROOT(E(u'html',
            E(u'head', E(u'title', 'SKOS browser')),
            E(u'body',
                E(u'div', dict(id=u"term"), node.xml_select(u'string(skos:prefLabel)')),
                ((
                    E(u'p', u'Broader terms:'),
                    E(u'ul', dict(id=u"broader"),
                        ( E(u'li',
                            E(u'a', dict(href=ref.xml_value.lstrip(self.baseuri)),
                                self.doc.xml_select(u'string(//skos:Concept[@rdf:about="%s"]/skos:prefLabel)'%ref.xml_value)
                            )
                        ) for ref in node.xml_select(u'skos:broader/@rdf:resource') )
                    )
                ) if node.xml_select(u'skos:broader') else () ),
                ((
                    E(u'p', u'Narrow terms:'),
                    E(u'ul', dict(id=u"narrower"),
                        ( E(u'li',
                            E(u'a', dict(href=ref.xml_value.lstrip(self.baseuri)),
                                self.doc.xml_select(u'string(//skos:Concept[@rdf:about="%s"]/skos:prefLabel)'%ref.xml_value)
                            )
                        ) for ref in node.xml_select(u'skos:narrower/@rdf:resource') )
                    )
                ) if node.xml_select(u'skos:narrower') else () )
            )
        )))
        return buf.getvalue()


def launch(skosfile, baseuri, default_concept=None):
    cherrypy.config.update({'server.socket_port': 9999})
    print >> sys.stderr, "Begin parsing"
    skostree = amara.parse(skosfile)
    print >> sys.stderr, "End parsing"
    cherrypy.quickstart(skos_handler(skostree, baseuri))
    return


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hF:v", ["help", "files="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		kwargs = {}
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-F", "--files"):
				kwargs['files'] = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

	launch(*args, **kwargs)


if __name__ == "__main__":
	sys.exit(main())

