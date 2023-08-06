from xm.hitcounter.interfaces import IHitcounter, IHitcountable
import time
import thread
from threading import Lock
lock = Lock()
cnt = 0

def hit_complete():
    global cnt
    lock.acquire()
    cnt += 1
    lock.release()

def hitOne(ob):
    o = IHitcounter(ob)
    o.hitCount()
    a = 1
    a += 1
    hit_complete()
    
def hitMany(ob, tc=50):
    while tc>0:
       tc -= 1
       thread.start_new_thread( hitOne, (ob,) )
       print "thread %d started" % tc

def test_performance(ob):
    global cnt
    start = time.time()
    steps = 20
    while steps>0:
        steps -= 1
        hitMany(ob)
        print "step", steps
    steps = 200
    while cnt<1000:
        time.sleep( 1 )
        print cnt  
    end = time.time()
    tot = end - start
    print "total : %dm %ds" % ( (int(tot))/60, tot%60)

#test_performance(None)
