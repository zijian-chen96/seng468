import threading, time

class StoppableThread(threading.Thread):
    def __init__(self, abc):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()
        self.abc = []
        self.abc.extend(abc)


    def run(self):
        while True:
            print(self.abc)
            if self.stopped():
                print(self.abc)
                print(abc)
                print("bye")
                return


    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()


a = {}
abc = [1,2,3,4,5]

ts = StoppableThread(abc)
ts.start()
time.sleep(2)
abc[2] = 6
#ts.stop()

a.update({'ggg':[ts]})
a.get('ggg')[-1].stop()
