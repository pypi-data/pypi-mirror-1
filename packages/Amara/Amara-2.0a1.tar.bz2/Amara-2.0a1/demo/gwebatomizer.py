from amara import bindery
import httplib2
import urllib, urllib2

class feedconverter(object):
    gfeed = "http://www.google.com/reader/atom/feed/%s"
    gfeed_limited = "http://www.google.com/reader/atom/feed/%s?r=n&n=%i"
    reader_prep_uri = "http://www.google.com/reader/api/0/token"
    def __init__(self, user, passwd):
        '''
        user - Google e-mail including the "@gmail.com"
        passwd - password
        '''
        #FIXME: might as well use httplib2 here as well
        # get an AuthToken from Google accounts
        # http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html#Parameters
        auth_uri = 'https://www.google.com/accounts/ClientLogin'
        authreq_data = urllib.urlencode({ "Email": user,
                                          "Passwd":  passwd,
                                          "service": "reader",
                                          "source":  "Amara demo",
                                          "accountType": "GOOGLE",
                                          #"continue": "http://www.google.com/",
                                          })
        auth_req = urllib2.Request(auth_uri, data=authreq_data)
        auth_resp = urllib2.urlopen(auth_req)
        auth_resp_body = auth_resp.read()
        auth_resp_dict = dict(x.split("=")
                              for x in auth_resp_body.split("\n") if x)
        self.auth = auth_resp_dict["Auth"].strip()
        self.sid = auth_resp_dict["SID"].strip()
        self.h = httplib2.Http()
        self.h.follow_all_redirects = True
        self._update_token()
        return

    def _update_token(self):
        headers = {'Cookie': 'SID='+self.sid}
        response, content = self.h.request(self.reader_prep_uri, 'GET', body=None, headers=headers)
        #print response, content
        self.token = response
        return
        
    def atomize(self, feed, count=None):
        headers = {'Cookie': 'SID=%s; T=%s'%(self.sid, self.token)}
        if count:
            response, content = self.h.request(self.gfeed_limited%(feed, count), 'GET', body=None, headers=headers)
        else:
            response, content = self.h.request(self.gfeed%(feed), 'GET', body=None, headers=headers)
        return content


if __name__ == '__main__':
    import sys
    feed = "http://www.thenervousbreakdown.com/uogbuji/feed/"

    user = sys.argv[1]
    passwd = sys.argv[2]
    fc = feedconverter(user, passwd)
    doc = bindery.parse(fc.atomize(feed, 10))
    print doc.feed.title

