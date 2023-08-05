#Test garbage collection

import unittest
import gc
import amara
from Ft.Xml import InputSource
from Ft.Lib import Uri

SCALE = 1000


class TestInterestingXmlPatterns(unittest.TestCase):
    def setUp(self):
        self.bigdoc1 = ["<A>"]
        self.bigdoc1.extend(["<B/>"]*(SCALE*100))
        self.bigdoc1.extend(["</A>"])
        self.bigdoc1 = ''.join(self.bigdoc1)
        #len(self.bigdoc1) is 400007 for SCALE = 1000
        gc.enable()
        return

    def testPushbindGC(self):
        #Use a simplistic trend eatcher to make sure that memory
        #Usage is not growing unreasonably
        #Cum is a measure of the cumulative growth trend in GC profile
        cum = 0.0
        elems = amara.pushbind(self.bigdoc1, u"B")
        init_gc = gc.collect()
        #print init_gc
        e = elems.next()
        iter1_gc = gc.collect()
        #print iter1_gc
        for i in xrange(100):
            e = elems.next()
            iter_gc = gc.collect()
            #print iter_gc
            try:
                increase = iter_gc - old_iter_gc
                #Uncomment the following lines for more info
                #if increase > 0:
                #    print "Increase ", increase, "(cumulative)", cum
                cum += increase
            except NameError:
                pass
            old_iter_gc = iter_gc
            self.assertEqual(cum/SCALE > 0.01, False)
        return


if __name__ == '__main__':
    unittest.main()


