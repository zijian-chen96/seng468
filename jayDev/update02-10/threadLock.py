import threading,sys



class finSystem(threading.Thread):
    def __init__(self, lock, a):
        threading.Thread.__init__(self)
        self.lock = lock
        self.a = a

    def run(self):
        #with self.lock:
        for i in range(5):
            self.lock.acquire()
            print('threading')
            self.a[2] = 6
            print('threading : ' + str(self.a))
            self.lock.release()


if __name__ == '__main__':
    lock = threading.Lock()
    global a
    a = [1,2,3,4,5]
    finSystem = finSystem(lock, a)
    finSystem.start()
    #finSystem.join()
    print(a)

    with lock:
        print('main')
        a[2] = 7
        print('main : ' + str(a))
