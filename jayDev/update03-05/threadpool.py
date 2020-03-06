from concurrent.futures import ThreadPoolExecutor
import threading
import time

def threadFunc(threadCount, dlist):
    while True:
        if len(dlist) > 0:
            print(threadCount)
            print(dlist)

            print(threadTracker)
            del threadTracker[threadCount]
            break

dic = {'user1':[1,2,3], 'user2':[4,5,6], 'user3':[7,8,9], 'user4':[10,11,12]}
executor = ThreadPoolExecutor(max_workers = 3)

threadTracker = {}

for k,v in dic.items():
    if len(threadTracker) < 3:
        future = executor.submit(threadFunc, k, v)
        threadTracker.update({k:future})
        #print(dic)
        #print(threadTracker)
        time.sleep(2)
    else:
        while True:
            if len(threadTracker) < 3:
                break

while True:
    pass
