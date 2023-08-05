import sys
from Ft.Xml import Sax
from Ft.Lib import Uri
from amara import saxtools

XHTML_NS = 'http://www.w3.org/1999/xhtml'

class xhtmlgen_consumer:
    """
    Encapsulation of a set of semi-co-routines designed to handle SAX events
    """
    def __init__(self):
        self.event = None
        self.top_dispatcher = {
           	(saxtools.START_ELEMENT, XHTML_NS, u'html'):
            self.handle_html,
            }
        return

    def handle_html(self, end_condition):
        dispatcher = {
            (saxtools.START_ELEMENT, XHTML_NS, u'head'):
            self.handle_head,
            (saxtools.START_ELEMENT, XHTML_NS, u'body'):
            self.handle_body,
            }
        #Initial call corresponds to the start html element
        curr_gen = None
        yield None
        while (curr_gen is not None) or (not self.event == end_condition):
            curr_gen = saxtools.tenorsax.event_loop_body(dispatcher, curr_gen, self.event)
            yield None
        #Element closed.  Wrap up
        raise StopIteration

    def handle_head(self, end_condition):
        dispatcher = {
            (saxtools.START_ELEMENT, XHTML_NS, 'title'):
            self.handle_title,
            }
        curr_gen = None
        print "Document head started."
        yield None
        while (curr_gen is not None) or (not self.event == end_condition):
            curr_gen = saxtools.tenorsax.event_loop_body(dispatcher, curr_gen, self.event)
            yield None
        #Element closed.  Wrap up
        print "Document head complete."
        raise StopIteration

    def handle_title(self, end_condition):
        yield None
        title = u''
        #No curr-gen because there are no child elements
        while not self.event == end_condition:
            if self.event[0] == saxtools.CHARACTER_DATA:
                title += self.params
            yield None
        #Element closed.  Wrap up
        print "Document title:", title
        raise StopIteration

    def handle_meta(self, end_condition):
        name = self.params.get((None, 'name'))
        content = self.params.get((None, 'content'))
        print "Meta name:", name, " content:"
        print content
        yield None
        return

    def handle_body(self, end_condition):
        dispatcher = {
            (saxtools.START_ELEMENT, XHTML_NS, 'p'):
            self.handle_p,
            }
        curr_gen = None
        print "Document body started."
        yield None
        while (curr_gen is not None) or (not self.event == end_condition):
            curr_gen = saxtools.tenorsax.event_loop_body(dispatcher, curr_gen, self.event)
            yield None
        #Element closed.  Wrap up
        print "Document body complete."
        raise StopIteration

    def handle_p(self, end_condition):
        yield None
        content = u''
        #No curr-gen because child elements are ignored
        while not self.event == end_condition:
            if self.event[0] == saxtools.CHARACTER_DATA:
                content += self.params
            yield None
        #Element closed.  Wrap up
        print "Document content para:", content
        raise StopIteration


if __name__ == "__main__":
    try:
        infile = sys.argv[1]
    except IndexError:
        infile = '../../demo/simple-xhtml.xml'
    parser = Sax.CreateParser()
    consumer = xhtmlgen_consumer()
    handler = saxtools.tenorsax(consumer)
    parser.setContentHandler(handler)
    parser.parse(Uri.OsPathToUri(infile))

