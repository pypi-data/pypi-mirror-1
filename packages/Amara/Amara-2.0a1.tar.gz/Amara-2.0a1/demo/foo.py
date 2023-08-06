BM1 = 'http://hg.4suite.org/amara/trunk/raw-file/bb6c40828b2d/demo/7days/bm1.xbel'
BM2 = 'http://hg.4suite.org/amara/trunk/raw-file/bb6c40828b2d/demo/7days/bm2.xbel'
from amara import bindery
s1 = bindery.parse(BM1).xml_select(u'string(//folder/title[.="XML"])')
s2 = bindery.parse(BM2).xml_select(u'string(//folder/title[.="XML"])')
print (s1, s2)
print s1 == s2

