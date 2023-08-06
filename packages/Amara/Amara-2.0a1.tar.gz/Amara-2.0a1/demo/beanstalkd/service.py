import sys
import time

# pybeanstalk imports
from beanstalk import serverconn
from beanstalk import job

#import amara
from amara.xslt import transform as transform_

from common import *

#def transform(source, transforms, params=None, output=None):
def transform(source=None, transforms=None, params=None):
    result = transform_(source, transforms[0], params=None)
    print source
    print transforms
    return result
    #return result.stream.read()

MENU = {
    BASEURI+'xslt': transform,
}


def consumer_main(connection):
    while True:
        connection.use(REQUEST_TUBE)
        j = connection.reserve()
        print j.data
        result = transform(j.data['source'], j.data['transforms'], j.data['params'])
        print result
        j.Finish()
        
        connection.use(j.data['response-tube'])
        j = job.Job(data=result, conn=connection)
        j.Queue()


def main():
    host = sys.argv[1].split(':')
    if len(host) == 2:
        server, port = host
    else:
        server = host
        port = '11300'
    port = int(port)

    print >> sys.stderr, 'Setting up connection'
    connection = serverconn.ServerConn(server, port)
    connection.job = job.Job
    consumer_main(connection)
    return

if __name__ == '__main__':
    main()

