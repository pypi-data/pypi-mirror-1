'''
>>> from client import *
>>> connect('localhost', 99988)
>>> print transform('<a><b/></a>', 'http://cvs.4suite.org/viewcvs/*checkout*/4Suite/Ft/Data/pretty.xslt')

'''

#from client import *; connect('localhost', 99988); print transform('<a><b/></a>', 'http://cvs.4suite.org/viewcvs/*checkout*/4Suite/Ft/Data/pretty.xslt')

import sys
import time

# pybeanstalk imports
from beanstalk import serverconn
from beanstalk import job

from amara.lib import inputsource

from common import *

g_connection = None

def transform(source, transforms, params=None):
    response_tube = 'RESPONSE' #You might decide to create one response tube per exchange
    request = {
        'type': BASEURI + 'xslt',
        'source': inputsource(source).stream.read(),
        'transforms': [inputsource(transforms).stream.read()],
        'params': params,
        'response-tube': response_tube,
    }
    g_connection.use(REQUEST_TUBE)
    j = job.Job(conn=g_connection)
    j.data = request
    j.Queue()

    g_connection.use(response_tube)
    j = g_connection.reserve()
    print j.data
    j.Finish()

    return j.data
    #return result.stream.read()


def connect(host, port):
    global g_connection
    g_connection = serverconn.ServerConn(host, port)
    g_connection.job = job.Job
    return


def main():
    host = sys.argv[1].split(':')
    if len(host) == 2:
        server, port = host
    else:
        server = host
        port = '11300'
    port = int(port)
    print >> sys.stderr, 'Setting up connection'
    connect(host, port)
    return


if __name__ == '__main__':
    main()

