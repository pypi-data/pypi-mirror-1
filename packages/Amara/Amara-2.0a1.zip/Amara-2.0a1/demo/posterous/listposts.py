from amara import bindery
from amara.writers.struct import *

PFEED = "http://uche.posterous.com/rss.xml"
feed = bindery.parse(PFEED)

w = structwriter(indent=u"yes")
w.feed(
ROOT(
    E(u'div',
        ( E(u'a', {u'href': unicode(it.link)}, unicode(it.title))
          for it in feed.rss.channel.item ),
    )
))

