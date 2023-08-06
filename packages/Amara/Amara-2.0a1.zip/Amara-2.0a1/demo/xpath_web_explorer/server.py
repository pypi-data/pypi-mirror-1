#!/usr/bin/env python
# encoding: utf-8
"""
xpath_web_explorer.py -- a demo server for simple access to an XML document set

Created by Uche Ogbuji on 2008-04-22.
Copyright 2008 Zepheira LLC
"""

import sys, re, os, sets, time, cgi, cStringIO
from wsgiref.util import shift_path_info, request_uri
from string import Template
import getopt
from itertools import *
from operator import *

import amara
from amara import writer
from amara.writers.struct import *
from amara.xslt import transform

help_message = '''
python server.py -F ./files
'''

DEFAULT_ROOT = 'files'

_404_PAGE = Template("""\
<html><body>
  <h1>404-ed!</h1>
  The requested URL <i>$url</i> was not found.
</body></html>""")


#for path, dirs, files in os.walk(root):
    #To skip any directory named 'etc':
    #if 'etc' in dirs:
    #    dirs.remove('etc')
    #You can also clear the dirs entirely: del dirs[:]
    

def process_get(environ):
    """
    Return a dict from QUERY_STRING
    """
    source = environ.get('QUERY_STRING', '')
    if not source:
        qparams = {}
    else:
        qparams = cgi.parse_qsl(source, keep_blank_values=True, strict_parsing=False)
    qparams = dict(((k, map(itemgetter(1), v)) for (k, v) in groupby(sorted(qparams), itemgetter(0))))
    return qparams

    #key = shift_path_info(environ) or 'index'


NS = u"http://purl.org/amara/demo1"


def xpath_explorer_app(environ, start_response):
    log = environ['wsgi.errors']
    qparams = process_get(environ)
    query = ''.join(qparams.get('xpath', []))
    #import pprint; pprint.pprint(environ)
    log = environ['wsgi.errors']
    root = xpath_explorer_app.files
    def fileiter(root, exclusions=None):
        exclusions = exclusions or []
        for path, dirs, files in os.walk(root):
            for excl in exclusions:
                if excl in dirs: dirs.remove(excl)
            for fname in files:
                yield fname

    filepath = environ['PATH_INFO'].lstrip('/')
    buf = cStringIO.StringIO()
    if filepath:
        requested_file = os.path.join(root, filepath)
        try:
            content = open(requested_file).read()
        except IOError:
            response = _404_PAGE.substitute(url=request_uri(environ))
            return [response]
        doc = amara.parse(content)
        if query:
            retval = doc.xml_select(query.decode('utf-8'))
            w = writer(stream=buf)
            w.start_document()
            w.start_element(NS, u'amara:result')
            for node in retval:
                buf.write()
                w.start_element(u'li')
                fname = fname.encode('utf-8')
                w.simple_element(u'a', attributes={u'href': fname}, content=fname)
                w.end_element(u'li')
            w.end_element(u'ul')
            w.end_element(u'body')
            w.end_element(NS, u'amara:result')
            w.end_document()
        else:
            pi = doc.xml_select(u'/processing-instruction("xml-stylesheet")')
            transforms = []
            if pi:
                pi = pi[0]
            else:
                transforms.append(os.path.join(DEFAULT_ROOT, 'xmlverbatimwrapper.xsl'))
            transform(os.path.join(DEFAULT_ROOT, filepath), transforms, output=buf)
        start_response('200 OK', [('content-type', 'text/html')])
        response = buf.getvalue()
        return [response]
    elif False:
        w = structwriter().feed(
        ROOT(E(u'html',
            E(u'head', E(u'title', 'XPath explorer')),
            E(u'body',
                E(u'form', dict(action=u".", method=u"post"), E(u'fieldset', E(u'legend', u'XPath explorer'),
                    E(u'label', {u"for": "xpath_exploring"}, 'Enter XPath'), #for references the id
                    #Use dict literal syntax due to problem keys "type" and "id"
                    E(u'input', {u"type": u"text", u"name": u"xpath", u"id": u"xpath", u"value": u""}),
                    E(u'input', {u"type": u"submit", u"name": u"submit", u"id": u"submit", u"value": u"Query"}),
                )),
                E(u'textarea', {u"height": u"200", u"width": u"200", u"id": u"result"},
                    ),
                #E(u'iframe', dict(src="http://example.com", height="200", width="200"),
                #    'Alternative text for browsers that do not understand IFrames.')
            )
        )))
        response = buf.getvalue()
        start_response('200 OK', [('content-type', 'application/xml')])
        return [response]
    else:
        #provide a list of files
        #FIXME: Explore/Use amara's capability here to generate elements from a generator
        #Import the basic writer class for users
        buf = cStringIO.StringIO()
        w = writer(stream=buf, method=u"html")
        w.start_document()
        w.start_element(u'html')
        w.start_element(u'head')
        w.simple_element(u'title', content=u'Available files')
        w.end_element(u'head')
        w.start_element(u'body')
        w.simple_element(u'h1', content=u"Available files")
        w.start_element(u'ul')
        for fname in fileiter(root):
            w.start_element(u'li')
            fname = fname.encode('utf-8')
            w.simple_element(u'a', attributes={u'href': fname}, content=fname)
            w.end_element(u'li')
        w.end_element(u'ul')
        w.end_element(u'body')
        w.end_element(u'html')
        w.end_document()
        response = buf.getvalue()
        print response
        start_response('200 OK', [('content-type', 'text/html')])
        return [response]


def launch(files="files"):
    global xpath_explorer_app
    from wsgiref import simple_server
    xpath_explorer_app.files = files

    #print 'sample usage:'
    print 'Start at: curl "http://localhost:8808/ (Note the trailing slash)"'
    print 'Also:\n\tcurl -i "http://localhost:8808/a.xml"'
    print 'Also:\n\tcurl -i "http://localhost:8808/a.xml?xpath=label[xml:id=%22co%22]"'
    
    #print '    curl --request POST --data-binary "@apache.log" --header "Content-Type: text/plain" "http://localhost:8808"'
    
    httpd = simple_server.WSGIServer(('', 8808), simple_server.WSGIRequestHandler)
    httpd.set_app(xpath_explorer_app)
    httpd.serve_forever()
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
