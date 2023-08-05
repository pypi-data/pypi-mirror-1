"""
A Web-based inspector of an XML document, using CherryPy and Amara
CherryPy is a brilliant and simple Web framework for Python
For more on CherryPy: http://www.cherrypy.org/
"""

import cStringIO

from amara import binderytools
from Ft.Xml.Domlette import Print, PrettyPrint
from xml.sax.saxutils import escape
from cherrypy import cpg


class xml_inspector:
    def __init__(self):
        self.url = None
        return

    def index(self):
        # Ask for the user's name.
        return '''
            <form action="get_expression" method="GET">
            <div>
            What XML file URL would you like to query
            <input type="text" name="url"/>
            <input type="submit" />
            </div>
            <div>As an example, try entering URL
            "http://uche.ogbuji.net/tech/4Suite/amara/monty.xml"
            and then querying for "monty.python"
            </div>
            </form>
        '''

    index.exposed = True

    def get_expression(self, url=None):
        if not url:
            url = self.url
        if url:
            #Don't re-retrieve the doc if it's already loaded
            if url != self.url:
                self.url = url
                self.doc = binderytools.bind_uri(url)
            return '''
            <form action="show_result" method="GET">
            Enter a Python expression for the XML query
            <input type="text" name="query"/>
            <input type="submit" />
            </form>
            '''
        else:
            # No URL was specified
            return "Please <a href='./'>go back</a> and enter a URL"

    get_expression.exposed = True


    def show_result(self, query=None):
        if query:
            stream = cStringIO.StringIO()
            PrettyPrint(eval("self.doc." + query), stream=stream)
            result = cStringIO.StringIO()
            result.write("<div>Resulting XML fragment:</div><div style='border: thin blue solid'>")
            result.write(escape(stream.getvalue()))
            result.write("</div>")
            result.write("<div>Please <a href='./get_expression'>go back</a> to try another expression, or <a href='./'>all the way back</a> to enter a new XML URL</div>")
            return result.getvalue()
        else:
            # No URL was specified
            return "Please <a href='./get_expression'>go back</a> and enter a URL"

    show_result.exposed = True


cpg.root = xml_inspector()
cpg.server.start(configFile='cherrypy.conf')

