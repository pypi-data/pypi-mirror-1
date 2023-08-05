"Use Pushbind to scour the Old testament for all verses containing the word 'begat' and print them"

#Download ot.xml (part of http://www.ibiblio.org/bosak/xml/eg/religion.2.00.xml.zip)

import gc
import time
import amara

for v in amara.pushbind('ot.xml', u'v'):
    text = unicode(v)
    if text.find('begat') != -1:
         print text.encode('utf-8')
         gc.collect()

#print "MAIN CODE COMPLETED.  WAITING 10 SECONDS"
#Allow for checking memory reclamation
#time.sleep(10)
#print "FORCING GARBAGE COLLECTION..."
#gc.collect()
#print "WAITING 10 SECONDS..."
#time.sleep(10)

